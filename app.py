import gradio as gr
from search_agent import ReActAgent
from config.prompts import SYSTEM_PROMPT, USER_PROMPT
from config.function_tools import web_search,get_location
from config.llm import get_llm


def create_agent():
    llm = get_llm()
    return ReActAgent(llm, tools=[web_search,get_location], max_steps=5)


def format_output(text: str) -> str:
    """格式化输出"""
    text = text.replace("Thought:", "\n\n**Thought:**")
    text = text.replace("Action Input:", "\n\n**Action Input:**")
    text = text.replace("Action:", "\n\n**Action:**")
    text = text.replace("Final Answer:", "\n\n**Final Answer:**")
    return text


def run_search(question, history, system_prompt, user_prompt):
    if not question.strip():
        yield "请输入问题"
        return

    agent = create_agent()
    output = ""

    for token in agent.run_stream(
            question=question,
            history=history,
            system_prompt=system_prompt if system_prompt.strip() else None,
            user_prompt=user_prompt if user_prompt.strip() else None
    ):
        output += token
        yield format_output(output)


css = """
.output-markdown {
    min-height: 400px;
    padding: 16px;
    border: 1px solid #e0e0e0;
    border-radius: 8px;
    background: #fafafa;
}
.prompt-box textarea {
    font-family: monospace;
    font-size: 12px;
}
"""

with gr.Blocks(title="基于ReAct范式的AI搜索") as demo:
    gr.Markdown("# 🔍AI搜索助手")

    with gr.Tab("搜索"):
        with gr.Row():
            with gr.Column(scale=2):
                question = gr.Textbox(
                    label="问题",
                    placeholder="输入你的问题...",
                    lines=2
                )
                search_btn = gr.Button("🔍 搜索", variant="primary", size="lg")

                output = gr.Markdown(
                    label="结果",
                    elem_classes=["output-markdown"]
                )

            with gr.Column(scale=1):
                history = gr.Textbox(
                    label="搜索历史 (可选)",
                    placeholder="用户的搜索历史，可以在提示词配置中对history占位符进行调优",
                    lines=8
                )

        gr.Examples(
            examples=[
                ["我附近有什么好吃的"],
                ["最近有什么AI领域的重大新闻"],
                ["川普今天说了什么"],
            ],
            inputs=[question]
        )

    with gr.Tab("提示词配置"):
        with gr.Row():
            system_prompt = gr.Textbox(
                label="System Prompt",
                value=SYSTEM_PROMPT,
                lines=20,
                elem_classes=["prompt-box"]
            )
            user_prompt = gr.Textbox(
                label="User Prompt",
                value=USER_PROMPT,
                lines=5,
                elem_classes=["prompt-box"]
            )

    search_btn.click(
        fn=run_search,
        inputs=[question, history, system_prompt, user_prompt],
        outputs=output
    )

    question.submit(
        fn=run_search,
        inputs=[question, history, system_prompt, user_prompt],
        outputs=output
    )

if __name__ == "__main__":
    demo.launch(share=True,server_port=7888,server_name="0.0.0.0")