import os

class PromptForgeAgent:
    """A lightweight, Python 3.9 compatible agent for video orchestration."""
    def __init__(self, role, goal, backstory, system_prompt, llm):
        self.role = role
        self.goal = goal
        self.backstory = backstory
        self.system_prompt = system_prompt
        self.llm = llm

    def execute(self, inputs):
        """Executes the agent's task using the provided LLM."""
        full_prompt = f"""
ROLE: {self.role}
GOAL: {self.goal}
BACKSTORY: {self.backstory}

{self.system_prompt}

INPUT DATA:
{inputs}

RESPONSE (Final JSON or text):
        """
        # Call llama-cpp-python directly
        response = self.llm(full_prompt, max_tokens=2000, stop=["\n\n\n"])
        return response['choices'][0]['text']

class VideoAgency:
    def __init__(self, llm):
        self.llm = llm
        self.agents = self._init_agents()

    def _init_agents(self):
        # Load prompts from files
        prompts = {}
        for p_name in ['analyzer', 'planner', 'renderer']:
            path = f'prompts/{p_name}_prompt.txt'
            if os.path.exists(path):
                with open(path, 'r', encoding='utf-8') as f:
                    prompts[p_name] = f.read()
            else:
                prompts[p_name] = f"Instructions for {p_name}"

        return {
            "analyst": PromptForgeAgent(
                role='Video Analyst',
                goal='Analyze raw assets and create a structured scene breakdown',
                backstory='Expert in film theory and scene analysis.',
                system_prompt=prompts.get('analyzer', ''),
                llm=self.llm
            ),
            "planner": PromptForgeAgent(
                role='Creative Director',
                goal='Create a comprehensive technical and creative plan',
                backstory='Hollywood-level film editor.',
                system_prompt=prompts.get('planner', ''),
                llm=self.llm
            ),
            "renderer": PromptForgeAgent(
                role='Technical Renderer',
                goal='Execute the rendering pipeline',
                backstory='Technical wizard mastering FFmpeg and ComfyUI.',
                system_prompt=prompts.get('renderer', ''),
                llm=self.llm
            )
        }

    def run_pipeline(self, raw_assets_context, profile="Vlog"):
        """Runs the sequential orchestration pipeline with Cinematic Profile awareness."""
        formatted_input = f"--- [ CINEMATIC PROFILE: {profile} ] ---\n\n{raw_assets_context}"
        
        print(f"🎬 Starting Analyst Stage [{profile}]...")
        analysis = self.agents["analyst"].execute(formatted_input)
        
        print(f"🎬 Starting Planner Stage [{profile}]...")
        plan = self.agents["planner"].execute(analysis)
        
        print(f"🎬 Starting Renderer Stage [{profile}]...")
        render_summary = self.agents["renderer"].execute(plan)
        
        return {
            "analysis": analysis,
            "plan": plan,
            "render_summary": render_summary
        }
