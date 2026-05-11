import json

class FrameworkContext:
    def __init__(self):
        self.requirements = ""
        self.architecture = ""
        self.code = ""
        self.test_results = ""
        self.documentation = ""

    def update_requirements(self, reqs: str):
        self.requirements = reqs

    def update_architecture(self, arch: str):
        self.architecture = arch

    def update_code(self, code: str):
        self.code = code

    def update_test_results(self, results: str):
        self.test_results = results

    def update_documentation(self, docs: str):
        self.documentation = docs

    def get_context_summary(self) -> str:
        return json.dumps({
            "requirements_set": bool(self.requirements),
            "architecture_set": bool(self.architecture),
            "code_set": bool(self.code),
            "tests_run": bool(self.test_results),
            "docs_generated": bool(self.documentation)
        })

    def to_dict(self):
        return {
            "requirements": self.requirements,
            "architecture": self.architecture,
            "code": self.code,
            "test_results": self.test_results,
            "documentation": self.documentation
        }
