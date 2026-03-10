"""
BaseNode — Foundation for all PocketFlow nodes.

Every node follows the prep/exec/post lifecycle:
- prep():  Prepare data from shared context
- exec():  Execute the core logic  
- post():  Store results back to context, return action string

This pattern comes from PocketFlow's Node abstraction.
"""


class BaseNode:
    """
    Base class for all nodes in the PocketFlow agent system.
    Each node must implement exec() at minimum.
    """

    def __init__(self, name: str):
        self.name = name

    def prep(self, context: dict) -> any:
        """Prepare data from shared context. Override for custom prep."""
        return context

    def exec(self, context: dict) -> any:
        """Execute the node's core logic. Must be implemented."""
        raise NotImplementedError(f"Node '{self.name}': exec() must be implemented")

    def post(self, context: dict, exec_result: any) -> str:
        """Store results and return action string. Default: 'default'."""
        context[f"result_{self.name}"] = exec_result
        return "default"

    def run(self, context: dict) -> str:
        """Full lifecycle: prep → exec → post."""
        prep_result = self.prep(context)
        exec_result = self.exec(context)
        action = self.post(context, exec_result)
        return action

    def __repr__(self):
        return f"<Node:{self.name}>"
