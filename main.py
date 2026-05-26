import json
import mimetypes
import os
import pathlib
import shlex
import subprocess
import tempfile
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass
class APIKeyStatus:
    name: str
    present: bool
    masked_value: str


class PersonalAIEmployee:
    """Safe, productivity-focused personal AI employee orchestrator."""

    def __init__(self, config_path: str = "config.json"):
        self.config_path = config_path
        self.config = self._load_config(config_path)
        self.session_log = pathlib.Path(self.config.get("session_log", "ai_employee_session.log"))
        self.workspace = pathlib.Path(self.config.get("workspace", "workspace"))
        self.workspace.mkdir(parents=True, exist_ok=True)
        self.api_status = self._read_api_status()
        self.devops = AutonomousDevTerminal(self)

    def _load_config(self, path: str) -> Dict[str, Any]:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _mask(self, value: Optional[str]) -> str:
        if not value:
            return "<not-set>"
        if len(value) <= 8:
            return "*" * len(value)
        return f"{value[:4]}...{value[-4:]}"

    def _read_api_status(self) -> List[APIKeyStatus]:
        keys = ["GEMINI_API_KEY", "HUGGINGFACE_KEY", "GITHUB_KEY", "GOOGLE_CLOUD_KEY"]
        return [
            APIKeyStatus(name=k, present=bool(os.getenv(k)), masked_value=self._mask(os.getenv(k)))
            for k in keys
        ]

    def health_report(self) -> Dict[str, Any]:
        report = {
            "assistant_name": self.config.get("assistant_name", "AI Employee"),
            "generated_at": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
            "api_keys": [status.__dict__ for status in self.api_status],
            "features": self.config.get("enabled_features", {}),
        }
        self._log_event("health_report", report)
        return report

    def choose_provider(self, task_type: str, has_file: bool = False, wants_voice: bool = False) -> str:
        task_type = task_type.lower().strip()
        if wants_voice:
            return "google_cloud" if os.getenv("GOOGLE_CLOUD_KEY") else "huggingface"
        if task_type in {"coding", "debugging", "repo", "github", "ci", "devops", "apk"}:
            return "github"
        if task_type in {"research", "analysis", "business", "income", "learning", "tutoring"}:
            return "gemini"
        if task_type in {"content", "creative", "marketing"}:
            return "huggingface" if os.getenv("HUGGINGFACE_KEY") else "gemini"
        if has_file:
            return "google_cloud" if os.getenv("GOOGLE_CLOUD_KEY") else "gemini"
        return "gemini"

    def process_file(self, file_path: str) -> Dict[str, Any]:
        path = pathlib.Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        mime_type, _ = mimetypes.guess_type(str(path))
        extension = path.suffix.lower()
        supported = {
            ".pdf": "Document understanding + summarization + Q&A",
            ".png": "Image understanding + OCR + captioning",
            ".jpg": "Image understanding + OCR + captioning",
            ".jpeg": "Image understanding + OCR + captioning",
            ".webp": "Image understanding + OCR + captioning",
            ".mp4": "Video transcription + timeline summary",
            ".mov": "Video transcription + timeline summary",
            ".docx": "Document parsing + key point extraction",
            ".txt": "Text summarization + action extraction",
        }

        result = {
            "file": str(path.resolve()),
            "size_bytes": path.stat().st_size,
            "mime_type": mime_type or "unknown",
            "detected_capability": supported.get(extension, "General file parsing"),
            "selected_provider": self.choose_provider(task_type="analysis", has_file=True),
            "next_steps": [
                "Extract raw content",
                "Run summarization and deep analysis",
                "Generate insights, action items, and opportunities",
                "Produce exportable markdown report",
            ],
        }

        self._log_event("process_file", result)
        return result

    def generate_income_plan(self, profile: Dict[str, Any]) -> Dict[str, Any]:
        skills = profile.get("skills", [])
        time_per_week = profile.get("hours_per_week", 10)

        ideas = [
            "Freelance technical writing with AI-assisted research",
            "Micro-SaaS feature prototyping and GitHub-based client delivery",
            "Automated content pipeline for niche blogs/newsletters",
            "AI tutoring or study-guide generation services",
            "Data labeling, evaluation, and prompt optimization gigs",
        ]

        plan = {
            "selected_provider": self.choose_provider("income"),
            "profile": profile,
            "recommended_tracks": ideas[:3] if time_per_week < 12 else ideas,
            "execution_system": {
                "daily": ["Lead sourcing + outreach", "Deliverable creation", "Learning + skill upgrade"],
                "weekly": ["Pipeline review", "Revenue tracking", "Automation improvements"],
            },
            "kpi": {
                "weekly_outreach_target": 30,
                "proposal_to_close_rate_goal": "10-20%",
                "monthly_revenue_goal": "$1,000-$5,000 (depends on skill depth)",
            },
            "notes": f"Profile skills considered: {', '.join(skills) if skills else 'generalist'}",
        }

        self._log_event("income_plan", plan)
        return plan

    def voice_stack_blueprint(self) -> Dict[str, Any]:
        blueprint = {
            "stt": {"primary": "Google Cloud Speech-to-Text", "fallback": "Hugging Face Whisper models"},
            "tts": {"primary": "Google Cloud Text-to-Speech", "fallback": "Hugging Face TTS models"},
            "realtime_conversation": {
                "transport": "WebSocket bi-directional audio stream",
                "agent_loop": ["User speech -> STT", "Intent + memory + tool routing", "Response generation", "TTS playback"],
            },
            "study_mode": {
                "description": "Speak tuition/study questions and receive natural spoken explanations with examples.",
                "adaptive_features": ["Difficulty adjustment", "Step-by-step reasoning mode", "Quiz generation"],
            },
        }
        self._log_event("voice_stack_blueprint", blueprint)
        return blueprint

    def task_router(self, task: str, task_type: str, file_path: Optional[str] = None, wants_voice: bool = False) -> Dict[str, Any]:
        provider = self.choose_provider(task_type=task_type, has_file=bool(file_path), wants_voice=wants_voice)
        response = {
            "task": task,
            "task_type": task_type,
            "file_path": file_path,
            "provider": provider,
            "status": "planned",
            "action_plan": [
                "Interpret objective and constraints",
                "Select best API/toolchain",
                "Execute with validation checks",
                "Return truthful, detailed output with assumptions noted",
            ],
        }
        self._log_event("task_router", response)
        return response

    def _log_event(self, event: str, payload: Dict[str, Any]):
        record = {"timestamp": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()), "event": event, "payload": payload}
        with open(self.session_log, "a", encoding="utf-8") as f:
            f.write(json.dumps(record) + "\n")


class AutonomousDevTerminal:
    """Dedicated terminal workspace for autonomous software engineering workflows."""

    def __init__(self, owner: PersonalAIEmployee):
        self.owner = owner
        self.root = owner.workspace / "autonomous_terminal"
        self.root.mkdir(parents=True, exist_ok=True)
        self.command_log = self.root / "terminal_commands.log"

    def capabilities(self) -> Dict[str, Any]:
        return {
            "supported_languages": self.owner.config.get("dev_terminal", {}).get("languages", []),
            "framework_ecosystems": self.owner.config.get("dev_terminal", {}).get("framework_ecosystems", []),
            "apk_build_support": {
                "android_stack": ["Java", "Kotlin", "Gradle", "Android SDK"],
                "cross_platform": ["Flutter", "React Native"],
                "status": "Blueprint ready; executes in environments with required SDKs installed.",
            },
            "autonomous_features": [
                "Code generation from task instructions",
                "Dependency installation plans",
                "Build/compile command execution",
                "Automatic error triage and retry",
                "Debug + optimization action checklist",
                "GitHub-ready push plan after explicit final approval",
            ],
        }

    def create_project_workspace(self, project_name: str) -> Dict[str, str]:
        safe_name = "".join(ch for ch in project_name.lower().replace(" ", "-") if ch.isalnum() or ch in "-_")
        project_path = self.root / safe_name
        (project_path / "src").mkdir(parents=True, exist_ok=True)
        (project_path / "build").mkdir(exist_ok=True)
        (project_path / "logs").mkdir(exist_ok=True)
        return {"project_name": safe_name, "project_path": str(project_path.resolve())}

    def execute_pipeline(self, project_path: str, commands: List[str], auto_fix: bool = True) -> Dict[str, Any]:
        results: List[Dict[str, Any]] = []
        path = pathlib.Path(project_path)

        for command in commands:
            cmd_list = shlex.split(command)
            run = subprocess.run(cmd_list, cwd=path, capture_output=True, text=True)
            result = {
                "command": command,
                "returncode": run.returncode,
                "stdout": run.stdout[-1200:],
                "stderr": run.stderr[-1200:],
            }
            results.append(result)
            self._log_command(result)

            if run.returncode != 0 and auto_fix:
                fix = self._suggest_fix(command, run.stderr)
                results.append({"command": command, "auto_fix_suggestion": fix, "status": "needs_review"})
                break

        return {"project_path": str(path.resolve()), "results": results}

    def _suggest_fix(self, command: str, stderr: str) -> str:
        error = stderr.lower()
        if "not found" in error:
            return f"Missing tool for `{command}`. Install required compiler/SDK/package manager and rerun."
        if "no such file" in error:
            return "Path/config issue detected. Verify project structure and build files."
        if "permission denied" in error:
            return "Permission issue detected. Ensure executable permissions and SDK access."
        if "dependency" in error or "module" in error:
            return "Dependency resolution failed. Run package-manager install and lock version compatibility."
        return "General build failure. Inspect stderr, run verbose mode, and retry with narrower step execution."

    def github_autopilot_plan(self, repo: str, branch: str = "main", final_approval: bool = False) -> Dict[str, Any]:
        authenticated = bool(os.getenv("GITHUB_KEY"))
        plan = {
            "repo": repo,
            "branch": branch,
            "github_key_present": authenticated,
            "final_approval_received": final_approval,
            "steps": [
                "Validate git status and run tests",
                "Create commit with generated changelog",
                "Authenticate using GitHub token",
                "Push branch and open PR",
                "Watch CI status and auto-triage dependency/workflow failures",
            ],
            "autonomous_push_status": "ready" if (authenticated and final_approval) else "waiting_for_approval_or_key",
        }
        self._log_command({"github_autopilot_plan": plan})
        return plan

    def _log_command(self, payload: Dict[str, Any]):
        with open(self.command_log, "a", encoding="utf-8") as f:
            f.write(json.dumps({"timestamp": time.time(), "payload": payload}) + "\n")


def run_demo() -> None:
    ai_employee = PersonalAIEmployee()
    print("=== Personal AI Employee: System Health ===")
    print(json.dumps(ai_employee.health_report(), indent=2))

    print("\n=== Autonomous Dev Terminal: Capabilities ===")
    print(json.dumps(ai_employee.devops.capabilities(), indent=2))

    print("\n=== Workspace Provisioning Demo ===")
    workspace = ai_employee.devops.create_project_workspace("Income APK Builder")
    print(json.dumps(workspace, indent=2))

    print("\n=== Task Routing Demo ===")
    route = ai_employee.task_router(
        task="Build a Kotlin Android APK and prepare CI pipeline.",
        task_type="apk",
    )
    print(json.dumps(route, indent=2))

    print("\n=== GitHub Autopilot Plan Demo ===")
    print(json.dumps(ai_employee.devops.github_autopilot_plan(repo="your-org/your-repo", final_approval=False), indent=2))


if __name__ == "__main__":
    run_demo()
