import json
import os
import re

from dotenv import load_dotenv
from openai import OpenAI
from playwright.sync_api import sync_playwright

from .tools import BrowserTools
from .prompts import SYSTEM_PROMPT

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

MAX_STEPS = 20


# ------------------------
# Response Parser
# ------------------------

def parse_response(text: str) -> dict:

    thought = re.search(
        r"THOUGHT:\s*(.+?)(?=ACTION:)",
        text,
        re.DOTALL,
    )

    action = re.search(
        r"ACTION:\s*(\w+)",
        text
    )

    params = re.search(
        r"PARAMS:\s*(\{.*\})",
        text,
        re.DOTALL,
    )

    params_str = params.group(1) if params else "{}"

    try:
        params_dict = json.loads(params_str)

    except json.JSONDecodeError:

        params_dict = {}

    return {

        "thought":
            thought.group(1).strip()
            if thought
            else "(no thought)",

        "action":
            action.group(1).strip()
            if action
            else "done",

        "params":
            params_dict,
    }


# ------------------------
# Action Dispatcher
# ------------------------

def dispatch(
    tools: BrowserTools,
    action: str,
    params: dict
) -> str:

    match action:

        case "navigate":
            return tools.navigate(
                params.get("url", "")
            )

        case "click":
            return tools.click(
                params.get("selector", "")
            )

        case "type":
            return tools.type_text(
                params.get("selector", ""),
                params.get("text", "")
            )

        case "scroll":
            return tools.scroll(
                params.get(
                    "direction",
                    "down"
                )
            )

        case "press_key":
            return tools.press_key(
                params.get(
                    "key",
                    "Enter"
                )
            )

        case "open_tab":
            return tools.open_tab(
                params.get("url", "")
            )

        case "switch_tab":
            return tools.switch_tab(
                int(
                    params.get(
                        "index",
                        0
                    )
                )
            )

        case "close_tab":
            return tools.close_tab(
                int(
                    params.get(
                        "index",
                        0
                    )
                )
            )

        case "list_tabs":
            return tools.list_tabs()

        case _:
            return "Unknown action."


# ------------------------
# Agent Runner
# ------------------------

def run_agent(
    task: str,
    headless: bool = True
):

    with sync_playwright() as p:

        browser = p.chromium.launch(
            headless=headless
        )

        try:

            context = browser.new_context(
                viewport={
                    "width": 1280,
                    "height": 800,
                }
            )

            context.new_page()

            tools = BrowserTools(
                context,
                client
            )

            messages = [

                {
                    "role": "system",
                    "content": SYSTEM_PROMPT,
                },

                {
                    "role": "user",
                    "content": task,
                },
            ]

            for step_num in range(
                1,
                MAX_STEPS + 1
            ):

                screenshot_b64 = (
                    tools.get_screenshot_b64()
                )

                dom_snapshot = (
                    tools.get_dom_snapshot()
                )

                tabs_info = json.loads(
                    tools.list_tabs()
                )

                messages.append(

                    {
                        "role": "user",

                        "content": [

                            {
                                "type": "image_url",

                                "image_url": {

                                    "url":
                                    f"data:image/png;base64,{screenshot_b64}",

                                    "detail":
                                    "low",
                                },
                            },

                            {

                                "type":
                                "text",

                                "text":
                                (
                                    f"Open tabs:\n"
                                    f"{json.dumps(tabs_info, indent=2)}\n\n"

                                    f"DOM Snapshot:\n"

                                    f"{json.dumps(dom_snapshot, indent=2)}"
                                ),
                            },
                        ],
                    }
                )

                response = client.chat.completions.create(

                    model="gpt-4o-mini",

                    messages=messages,

                    max_tokens=1024,
                )

                reply_text = (
                    response
                    .choices[0]
                    .message.content
                )

                parsed = parse_response(
                    reply_text
                )

                action = parsed["action"]

                params = parsed["params"]

                thought = parsed["thought"]


                # done

                if action == "done":

                    result = params.get(
                        "result",
                        "Task completed."
                    )

                    yield {

                        "type":
                        "done",

                        "step":
                        step_num,

                        "thought":
                        thought,

                        "action":
                        "done",

                        "params":
                        params,

                        "observation":
                        result,

                        "screenshot":
                        screenshot_b64,

                        "tabs":
                        tabs_info,

                        "result":
                        result,
                    }

                    return


                # execute action

                observation = dispatch(
                    tools,
                    action,
                    params,
                )


                yield {

                    "type":
                    "step",

                    "step":
                    step_num,

                    "thought":
                    thought,

                    "action":
                    action,

                    "params":
                    params,

                    "observation":
                    observation,

                    "screenshot":
                    screenshot_b64,

                    "tabs":
                    tabs_info,
                }


                messages.append(

                    {
                        "role":
                        "assistant",

                        "content":
                        reply_text,
                    }
                )

                messages.append(

                    {
                        "role":
                        "user",

                        "content":
                        f"Observation: {observation}",
                    }
                )

            yield {

                "type":
                "error",

                "step":
                MAX_STEPS,

                "thought":
                "Max steps reached",

                "action":
                "done",

                "params":
                {},

                "observation":
                "Agent stopped: maximum steps reached.",

                "screenshot":
                tools.get_screenshot_b64(),

                "tabs":
                json.loads(
                    tools.list_tabs()
                ),

                "result":
                "Max steps reached.",
            }

        finally:

            browser.close()