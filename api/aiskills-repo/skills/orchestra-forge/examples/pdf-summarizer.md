# Orchestra Forge — Usage Example

## Example: "I want an agent that summarizes PDF documents"

### Phase 1 — ARCHITECT output

```yaml
agent:
  name: "PDFSummarizerAgent"
  description: "Loads PDF documents, chunks them, and produces structured summaries."
  univers:
    - PocketFlowCore
    - StructureAgentIA
    - RAGUnivers
  protocol: N2A
  llm: claude-sonnet-4-5
  memory: false
  eventbus: false
  scheduler: false
  metrics: true
  tracing: false

flows:
  - name: summarize
    nodes:
      - LoadPDF
      - ChunkText
      - SummarizeChunk
      - AggregateOutput
    transitions:
      - from: LoadPDF
        to: ChunkText
        on: default
      - from: ChunkText
        to: SummarizeChunk
        on: default
      - from: SummarizeChunk
        to: AggregateOutput
        on: default
```

---

### Phase 2 — SCAFFOLD output

```python
from pocketflow import Node, BatchNode, Flow

class LoadPDF(Node):
    def prep(self, shared):
        return shared["pdf_path"]

    def exec(self, path):
        import pathlib
        return pathlib.Path(path).read_text(encoding="utf-8", errors="ignore")

    def post(self, shared, prep_res, exec_res):
        shared["raw_text"] = exec_res
        return "default"


class ChunkText(Node):
    CHUNK_SIZE = 1500

    def prep(self, shared):
        return shared["raw_text"]

    def exec(self, text):
        return [text[i:i+self.CHUNK_SIZE] for i in range(0, len(text), self.CHUNK_SIZE)]

    def post(self, shared, prep_res, exec_res):
        shared["chunks"] = exec_res
        return "default"


class SummarizeChunk(BatchNode):
    def prep(self, shared):
        return shared["chunks"]

    def exec(self, chunk):
        return call_llm(f"Summarize this text concisely:\n\n{chunk}")

    def post(self, shared, prep_res, exec_res):
        shared["summaries"] = exec_res  # list of summaries
        return "default"


class AggregateOutput(Node):
    def prep(self, shared):
        return shared["summaries"]

    def exec(self, summaries):
        combined = "\n\n".join(summaries)
        return call_llm(f"Merge these summaries into one coherent document:\n\n{combined}")

    def post(self, shared, prep_res, exec_res):
        shared["final_summary"] = exec_res
        return "default"


# Wire the flow
load = LoadPDF(max_retries=2)
chunk = ChunkText()
summarize = SummarizeChunk(max_retries=3, wait=1)
aggregate = AggregateOutput(max_retries=2)

load >> chunk >> summarize >> aggregate
flow = Flow(start=load)

# Run
if __name__ == "__main__":
    shared = {"pdf_path": "document.pdf"}
    flow.run(shared)
    print(shared["final_summary"])
```

---

### Phase 3 — FORGE findings

| Role | Finding |
|------|---------|
| Architecture Analyst | ✅ All universes mapped to nodes. `RAGUnivers` represented by `ChunkText` + `SummarizeChunk`. |
| Code Refactorer | ✅ `CHUNK_SIZE` made configurable. `max_retries` added on LLM nodes. |
| Skill Reviewer | ⚠️ `BatchNode` could be `AsyncParallelBatchNode` for large PDFs — flag as enhancement. |
| Security Auditor | ✅ `pdf_path` from shared (not user raw input). No shell injection risk. |
| Documentation | ✅ Docstrings added. Usage example included. |
