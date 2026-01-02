import re
import json
from datetime import datetime
from jinja2 import Template
from config.prompts import SYSTEM_PROMPT, USER_PROMPT


class ReActAgent:
    def __init__(self, llm, tools: list, max_steps: int = 5):
        self.llm = llm
        self.tools = {t.name: t for t in tools}
        self.max_steps = max_steps

    def _format_tools(self) -> str:
        lines = []
        for name, t in self.tools.items():
            lines.append(f"### {name}")
            lines.append(t.description)
            if hasattr(t, 'args_schema') and t.args_schema:
                schema = t.args_schema.model_json_schema()
                lines.append("参数:")
                for param, info in schema.get('properties', {}).items():
                    req = "必填" if param in schema.get('required', []) else "可选"
                    desc = info.get('description', '')
                    default = info.get('default')
                    enum = info.get('enum')
                    extra = []
                    if enum:
                        extra.append(f"可选值: {enum}")
                    if default:
                        extra.append(f"默认: {default}")
                    extra_str = f" ({', '.join(extra)})" if extra else ""
                    lines.append(f"  - {param} [{req}]: {desc}{extra_str}")
            lines.append("")
        return "\n".join(lines)

    def _render_prompt(self, template: str, **context) -> str:
        return Template(template).render(**context)

    def _parse_action_input(self, raw: str) -> dict:
        raw = raw.strip()
        try:
            return json.loads(raw)
        except:
            pass
        json_match = re.search(r'\{[^{}]+\}', raw)
        if json_match:
            try:
                return json.loads(json_match.group())
            except:
                pass
        try:
            return json.loads(raw.replace("'", '"'))
        except:
            pass
        return {"query": raw.strip('"\'').strip()}

    def _call_tool(self, name: str, params: dict) -> str:
        if name not in self.tools:
            return f"[Error] 工具 '{name}' 不存在"
        try:
            result = self.tools[name].invoke(params)
            return result[:1500] + "..." if len(result) > 1500 else result
        except Exception as e:
            return f"[Error] {str(e)}"

    def run_stream(self, question: str, history: str = "",
                   system_prompt: str = None, user_prompt: str = None):
        """流式运行"""
        system_tpl = system_prompt or SYSTEM_PROMPT
        user_tpl = user_prompt or USER_PROMPT

        context = {
            "current_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "tools": self._format_tools()
        }
        system = self._render_prompt(system_tpl, **context)

        accumulated_history = history

        for step in range(self.max_steps):
            yield f"\n\n---\n\n### Step {step + 1}\n\n"

            is_last_step = (step == self.max_steps - 1)
            if is_last_step:
                accumulated_history += "\n\n[系统提示] 这是最后一步，请根据已有信息输出 Final Answer。"

            user_context = {"question": question, "history": accumulated_history}
            user = self._render_prompt(user_tpl, **user_context)

            messages = [
                {"role": "system", "content": system},
                {"role": "user", "content": user}
            ]

            full_text = ""
            stop_word = "Observation:"

            for chunk in self.llm.stream(messages):
                token = chunk.content
                full_text += token

                # 检测 stop word
                if not is_last_step and stop_word in full_text:
                    full_text = full_text.split(stop_word)[0]
                    break

                yield token  # 直接输出原文，不做替换

            parsed = self._parse_full_output(full_text)

            if parsed.get("final_answer"):
                return

            if is_last_step:
                if not parsed.get("final_answer"):
                    yield "\n\n**Final Answer:** " + (parsed.get("thought") or "无法生成答案")
                return

            if parsed.get("action") and parsed.get("action_input") is not None:
                observation = self._call_tool(parsed["action"], parsed["action_input"])
                yield f"\n\n**Observation:**\n\n[{observation}]\n\n"

                accumulated_history += f"\nThought: {parsed.get('thought', '')}"
                accumulated_history += f"\nAction: {parsed['action']}"
                accumulated_history += f"\nAction Input: {json.dumps(parsed['action_input'], ensure_ascii=False)}"
                accumulated_history += f"\nObservation: {observation}"
            else:
                yield "\n\n⚠️ 未解析到有效Action\n"
                accumulated_history += f"\nThought: {parsed.get('thought', '')}\n[系统提示] 请按格式输出Action和Action Input"

    def _parse_full_output(self, text: str) -> dict:
        result = {"thought": None, "action": None, "action_input": None, "final_answer": None}

        final_match = re.search(r"Final Answer:\s*(.+)", text, re.S)
        if final_match:
            result["final_answer"] = final_match.group(1).strip()
            thought_match = re.search(r"Thought:\s*(.+?)(?=Final Answer:)", text, re.S)
            if thought_match:
                result["thought"] = thought_match.group(1).strip()
            return result

        thought_match = re.search(r"Thought:\s*(.+?)(?=Action:|$)", text, re.S)
        if thought_match:
            result["thought"] = thought_match.group(1).strip()

        action_match = re.search(r"Action:\s*(\w+)", text)
        if action_match:
            result["action"] = action_match.group(1).strip()

        input_match = re.search(r"Action Input:\s*(.+?)(?=Observation:|Thought:|$)", text, re.S)
        if input_match:
            result["action_input"] = self._parse_action_input(input_match.group(1).strip())

        return result
