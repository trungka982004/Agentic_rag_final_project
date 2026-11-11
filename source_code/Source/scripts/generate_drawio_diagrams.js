const fs = require('fs');
const path = require('path');
const zlib = require('zlib');

// Output directories at project root
const ROOT = path.resolve(__dirname, '../../../');
const DIRS = [
  path.join(ROOT, 'manuscripts/paper1_springer_nature/figures'),
  path.join(ROOT, 'manuscripts/paper2_software_impacts/figures')
];

DIRS.forEach(dir => {
  if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
});

// Helper to escape XML
function xmlEscape(str) {
  return str
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&apos;');
}

// -----------------------------------------------------------------------------
// DIAGRAM 1: Overall System Architecture (fig1_overall_architecture.drawio)
// -----------------------------------------------------------------------------
function buildFig1XML() {
  return `<mxGraphModel dx="1400" dy="850" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="1350" pageHeight="750" background="#FFFFFF" math="0" shadow="0">
  <root>
    <mxCell id="0"/>
    <mxCell id="1" parent="0"/>
    
    <!-- User Input -->
    <mxCell id="node_input" value="&lt;b&gt;User Query (q)&lt;/b&gt;&lt;br&gt;&lt;font style=&quot;font-size: 11px; color: #475569;&quot;&gt;Raw Query Stream / UI&lt;/font&gt;" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#EFF6FF;strokeColor=#3B82F6;strokeWidth=2;fontSize=13;fontFamily=Helvetica;fontColor=#1E293B;" vertex="1" parent="1">
      <mxGeometry x="40" y="270" width="160" height="70" as="geometry"/>
    </mxCell>

    <!-- Router Node -->
    <mxCell id="node_router" value="&lt;b&gt;Router Node (δ&lt;sub&gt;router&lt;/sub&gt;)&lt;/b&gt;&lt;br&gt;&lt;font style=&quot;font-size: 11px; color: #475569;&quot;&gt;Heuristic + Qwen2.5-7B&lt;br&gt;Intent Classifier&lt;/font&gt;" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#EEF2FF;strokeColor=#6366F1;strokeWidth=2;fontSize=13;fontFamily=Helvetica;fontColor=#1E293B;" vertex="1" parent="1">
      <mxGeometry x="250" y="260" width="180" height="90" as="geometry"/>
    </mxCell>

    <!-- Tier 1: Local Corpus -->
    <mxCell id="node_tier1" value="&lt;b&gt;Tier 1: Local Knowledge Corpus&lt;/b&gt;&lt;br&gt;&lt;font style=&quot;font-size: 11px; color: #065F46;&quot;&gt;ChromaDB (Dense) + BM25 (Sparse)&lt;br&gt;Weighted RRF (k=60, w=0.7/0.3)&lt;br&gt;618 Papers | 144k Chunks&lt;/font&gt;" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#ECFDF5;strokeColor=#10B981;strokeWidth=2;fontSize=13;fontFamily=Helvetica;fontColor=#064E3B;" vertex="1" parent="1">
      <mxGeometry x="490" y="60" width="260" height="90" as="geometry"/>
    </mxCell>

    <!-- Tier 3: Expert Synthesis -->
    <mxCell id="node_tier3" value="&lt;b&gt;Tier 3: Expert Academic Synthesis&lt;/b&gt;&lt;br&gt;&lt;font style=&quot;font-size: 11px; color: #5B21B6;&quot;&gt;Tavily Academic Search API&lt;br&gt;Cross-Paper Literature Synthesis&lt;/font&gt;" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#F5F3FF;strokeColor=#8B5CF6;strokeWidth=2;fontSize=13;fontFamily=Helvetica;fontColor=#4C1D95;" vertex="1" parent="1">
      <mxGeometry x="490" y="200" width="260" height="75" as="geometry"/>
    </mxCell>

    <!-- Tier 2: Web Search Fallback -->
    <mxCell id="node_tier2" value="&lt;b&gt;Tier 2: Web Search Fallback&lt;/b&gt;&lt;br&gt;&lt;font style=&quot;font-size: 11px; color: #92400E;&quot;&gt;DuckDuckGo Search API&lt;br&gt;Triggered on Local Low Overlap&lt;/font&gt;" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#FFFBEB;strokeColor=#F59E0B;strokeWidth=2;fontSize=13;fontFamily=Helvetica;fontColor=#78350F;" vertex="1" parent="1">
      <mxGeometry x="490" y="325" width="260" height="75" as="geometry"/>
    </mxCell>

    <!-- REPL Sandbox -->
    <mxCell id="node_repl" value="&lt;b&gt;Python REPL Sandbox (v&lt;sub&gt;repl&lt;/sub&gt;)&lt;/b&gt;&lt;br&gt;&lt;font style=&quot;font-size: 11px; color: #9D174D;&quot;&gt;Deterministic Math &amp;amp; Code&lt;br&gt;Process-Isolated Execution&lt;/font&gt;" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#FDF2F8;strokeColor=#EC4899;strokeWidth=2;fontSize=13;fontFamily=Helvetica;fontColor=#831843;" vertex="1" parent="1">
      <mxGeometry x="490" y="450" width="260" height="75" as="geometry"/>
    </mxCell>

    <!-- Relevance Grader -->
    <mxCell id="node_grader" value="&lt;b&gt;Relevance Grader (δ&lt;sub&gt;grader&lt;/sub&gt;)&lt;/b&gt;&lt;br&gt;&lt;font style=&quot;font-size: 11px; color: #9A3412;&quot;&gt;Token Set Overlap Metric&lt;br&gt;Threshold τ ≥ 0.25&lt;/font&gt;" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#FFF7ED;strokeColor=#EA580C;strokeWidth=2;fontSize=13;fontFamily=Helvetica;fontColor=#7C2D12;" vertex="1" parent="1">
      <mxGeometry x="810" y="60" width="200" height="90" as="geometry"/>
    </mxCell>

    <!-- LLM Generator -->
    <mxCell id="node_generator" value="&lt;b&gt;LLM Generator Node&lt;/b&gt;&lt;br&gt;&lt;font style=&quot;font-size: 11px; color: #064E3B;&quot;&gt;Qwen2.5-7B Instruct&lt;br&gt;Grounded Response Synthesis&lt;br&gt;&lt;b style=&quot;color: #DC2626;&quot;&gt;Self-Correction Loop (r ≤ 2)&lt;/b&gt;&lt;/font&gt;" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#ECFDF5;strokeColor=#059669;strokeWidth=2;fontSize=13;fontFamily=Helvetica;fontColor=#064E3B;" vertex="1" parent="1">
      <mxGeometry x="810" y="250" width="200" height="110" as="geometry"/>
    </mxCell>

    <!-- Grounded Output -->
    <mxCell id="node_output" value="&lt;b&gt;Grounded Stream Output&lt;/b&gt;&lt;br&gt;&lt;font style=&quot;font-size: 11px; color: #1E293B;&quot;&gt;WebSocket Markdown Stream&lt;br&gt;Click-to-Verify Citations&lt;/font&gt;" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#F8FAFC;strokeColor=#475569;strokeWidth=2;fontSize=13;fontFamily=Helvetica;fontColor=#0F172A;" vertex="1" parent="1">
      <mxGeometry x="1070" y="270" width="200" height="70" as="geometry"/>
    </mxCell>

    <!-- Connectors -->
    <!-- Input -> Router -->
    <mxCell id="edge_in_router" style="edgeStyle=orthogonalEdgeStyle;rounded=1;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#3B82F6;strokeWidth=2.5;" edge="1" parent="1" source="node_input" target="node_router">
      <mxGeometry relative="1" as="geometry"/>
    </mxCell>

    <!-- Router -> Tier 1 -->
    <mxCell id="edge_r_t1" value="Local Query" style="edgeStyle=orthogonalEdgeStyle;rounded=1;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#10B981;strokeWidth=2;fontSize=11;fontStyle=1;fontColor=#047857;" edge="1" parent="1" source="node_router" target="node_tier1">
      <mxGeometry relative="1" as="geometry"/>
    </mxCell>

    <!-- Router -> Tier 3 -->
    <mxCell id="edge_r_t3" value="Comparative" style="edgeStyle=orthogonalEdgeStyle;rounded=1;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#8B5CF6;strokeWidth=2;fontSize=11;fontStyle=1;fontColor=#6D28D9;" edge="1" parent="1" source="node_router" target="node_tier3">
      <mxGeometry relative="1" as="geometry"/>
    </mxCell>

    <!-- Router -> Tier 2 (rare direct) -->
    <mxCell id="edge_r_t2" value="Web Fallback" style="edgeStyle=orthogonalEdgeStyle;rounded=1;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#F59E0B;strokeWidth=1.5;strokeDashArray=3 3;fontSize=11;fontColor=#B45309;" edge="1" parent="1" source="node_router" target="node_tier2">
      <mxGeometry relative="1" as="geometry"/>
    </mxCell>

    <!-- Router -> REPL -->
    <mxCell id="edge_r_repl" value="Math / Code" style="edgeStyle=orthogonalEdgeStyle;rounded=1;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#EC4899;strokeWidth=2;fontSize=11;fontStyle=1;fontColor=#BE185D;" edge="1" parent="1" source="node_router" target="node_repl">
      <mxGeometry relative="1" as="geometry"/>
    </mxCell>

    <!-- Tier 1 -> Grader -->
    <mxCell id="edge_t1_grader" style="edgeStyle=orthogonalEdgeStyle;rounded=1;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#10B981;strokeWidth=2;" edge="1" parent="1" source="node_tier1" target="node_grader">
      <mxGeometry relative="1" as="geometry"/>
    </mxCell>

    <!-- Grader Pass -> Generator -->
    <mxCell id="edge_grader_pass" value="Pass (Overlap ≥ 0.25)" style="edgeStyle=orthogonalEdgeStyle;rounded=1;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#059669;strokeWidth=2;fontSize=11;fontStyle=1;fontColor=#047857;" edge="1" parent="1" source="node_grader" target="node_generator">
      <mxGeometry relative="1" as="geometry"/>
    </mxCell>

    <!-- Grader Fail -> Tier 2 Fallback -->
    <mxCell id="edge_grader_fail" value="Fail (Overlap &lt; 0.25)" style="edgeStyle=orthogonalEdgeStyle;rounded=1;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#EA580C;strokeWidth=2;dashed=1;fontSize=11;fontStyle=1;fontColor=#C2410C;" edge="1" parent="1" source="node_grader" target="node_tier2">
      <mxGeometry relative="1" as="geometry">
        <Array as="points">
          <mxPoint x="910" y="180"/>
          <mxPoint x="790" y="180"/>
          <mxPoint x="790" y="360"/>
        </Array>
      </mxGeometry>
    </mxCell>

    <!-- Tier 3 -> Generator -->
    <mxCell id="edge_t3_gen" style="edgeStyle=orthogonalEdgeStyle;rounded=1;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#8B5CF6;strokeWidth=2;" edge="1" parent="1" source="node_tier3" target="node_generator">
      <mxGeometry relative="1" as="geometry"/>
    </mxCell>

    <!-- Tier 2 -> Generator -->
    <mxCell id="edge_t2_gen" style="edgeStyle=orthogonalEdgeStyle;rounded=1;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#F59E0B;strokeWidth=2;" edge="1" parent="1" source="node_tier2" target="node_generator">
      <mxGeometry relative="1" as="geometry"/>
    </mxCell>

    <!-- REPL -> Generator -->
    <mxCell id="edge_repl_gen" style="edgeStyle=orthogonalEdgeStyle;rounded=1;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#EC4899;strokeWidth=2;" edge="1" parent="1" source="node_repl" target="node_generator">
      <mxGeometry relative="1" as="geometry">
        <Array as="points">
          <mxPoint x="780" y="490"/>
          <mxPoint x="780" y="330"/>
        </Array>
      </mxGeometry>
    </mxCell>

    <!-- Generator Self-Correction Loop -->
    <mxCell id="edge_self_correct" value="Hallucination Retry (r ≤ 2)" style="edgeStyle=orthogonalEdgeStyle;rounded=1;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#DC2626;strokeWidth=2.5;dashed=1;fontSize=11;fontStyle=1;fontColor=#B91C1C;" edge="1" parent="1" source="node_generator" target="node_generator">
      <mxGeometry relative="1" as="geometry">
        <Array as="points">
          <mxPoint x="910" y="400"/>
          <mxPoint x="1030" y="400"/>
          <mxPoint x="1030" y="270"/>
        </Array>
      </mxGeometry>
    </mxCell>

    <!-- Generator -> Output -->
    <mxCell id="edge_gen_out" style="edgeStyle=orthogonalEdgeStyle;rounded=1;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#059669;strokeWidth=2.5;" edge="1" parent="1" source="node_generator" target="node_output">
      <mxGeometry relative="1" as="geometry"/>
    </mxCell>

  </root>
</mxGraphModel>`;
}

// -----------------------------------------------------------------------------
// DIAGRAM 2: LangGraph State Machine Graph G = (V, E, S) (fig2_langgraph_state_machine.drawio)
// -----------------------------------------------------------------------------
function buildFig2XML() {
  return `<mxGraphModel dx="1400" dy="850" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="1350" pageHeight="700" background="#FFFFFF" math="0" shadow="0">
  <root>
    <mxCell id="0"/>
    <mxCell id="1" parent="0"/>

    <!-- START -->
    <mxCell id="node_start" value="&lt;b&gt;START&lt;/b&gt;" style="ellipse;whiteSpace=wrap;html=1;fillColor=#1E293B;strokeColor=#0F172A;fontSize=12;fontColor=#FFFFFF;fontFamily=Helvetica;" vertex="1" parent="1">
      <mxGeometry x="40" y="280" width="80" height="50" as="geometry"/>
    </mxCell>

    <!-- v_router -->
    <mxCell id="node_v_router" value="&lt;b&gt;v&lt;sub&gt;router&lt;/sub&gt;&lt;/b&gt;&lt;br&gt;&lt;font style=&quot;font-size: 11px;&quot;&gt;Query Intent Router&lt;/font&gt;" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#EEF2FF;strokeColor=#4F46E5;strokeWidth=2;fontSize=13;fontFamily=Helvetica;fontColor=#1E293B;" vertex="1" parent="1">
      <mxGeometry x="170" y="270" width="160" height="70" as="geometry"/>
    </mxCell>

    <!-- v_retrieve -->
    <mxCell id="node_v_retrieve" value="&lt;b&gt;v&lt;sub&gt;retrieve&lt;/sub&gt;&lt;/b&gt;&lt;br&gt;&lt;font style=&quot;font-size: 11px; color: #065F46;&quot;&gt;Local Hybrid (RRF)&lt;/font&gt;" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#ECFDF5;strokeColor=#059669;strokeWidth=2;fontSize=13;fontFamily=Helvetica;fontColor=#064E3B;" vertex="1" parent="1">
      <mxGeometry x="430" y="70" width="180" height="70" as="geometry"/>
    </mxCell>

    <!-- v_expert -->
    <mxCell id="node_v_expert" value="&lt;b&gt;v&lt;sub&gt;expert&lt;/sub&gt;&lt;/b&gt;&lt;br&gt;&lt;font style=&quot;font-size: 11px; color: #5B21B6;&quot;&gt;Tavily Academic Query&lt;/font&gt;" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#F5F3FF;strokeColor=#7C3AED;strokeWidth=2;fontSize=13;fontFamily=Helvetica;fontColor=#4C1D95;" vertex="1" parent="1">
      <mxGeometry x="430" y="200" width="180" height="70" as="geometry"/>
    </mxCell>

    <!-- v_repl -->
    <mxCell id="node_v_repl" value="&lt;b&gt;v&lt;sub&gt;repl&lt;/sub&gt;&lt;/b&gt;&lt;br&gt;&lt;font style=&quot;font-size: 11px; color: #9D174D;&quot;&gt;Python REPL Sandbox&lt;/font&gt;" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#FDF2F8;strokeColor=#DB2777;strokeWidth=2;fontSize=13;fontFamily=Helvetica;fontColor=#831843;" vertex="1" parent="1">
      <mxGeometry x="430" y="470" width="180" height="70" as="geometry"/>
    </mxCell>

    <!-- v_grade -->
    <mxCell id="node_v_grade" value="&lt;b&gt;v&lt;sub&gt;grade&lt;/sub&gt;&lt;/b&gt;&lt;br&gt;&lt;font style=&quot;font-size: 11px; color: #9A3412;&quot;&gt;Relevance Grader&lt;/font&gt;" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#FFF7ED;strokeColor=#D97706;strokeWidth=2;fontSize=13;fontFamily=Helvetica;fontColor=#7C2D12;" vertex="1" parent="1">
      <mxGeometry x="690" y="70" width="180" height="70" as="geometry"/>
    </mxCell>

    <!-- v_web -->
    <mxCell id="node_v_web" value="&lt;b&gt;v&lt;sub&gt;web&lt;/sub&gt;&lt;/b&gt;&lt;br&gt;&lt;font style=&quot;font-size: 11px; color: #9A3412;&quot;&gt;DuckDuckGo Fallback&lt;/font&gt;" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#FFFBEB;strokeColor=#EA580C;strokeWidth=2;fontSize=13;fontFamily=Helvetica;fontColor=#78350F;" vertex="1" parent="1">
      <mxGeometry x="690" y="200" width="180" height="70" as="geometry"/>
    </mxCell>

    <!-- v_generate -->
    <mxCell id="node_v_generate" value="&lt;b&gt;v&lt;sub&gt;generate&lt;/sub&gt;&lt;/b&gt;&lt;br&gt;&lt;font style=&quot;font-size: 11px; color: #044E54;&quot;&gt;LLM Synthesis Node&lt;br&gt;(Qwen2.5-7B)&lt;/font&gt;" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#F0FDFA;strokeColor=#0D9488;strokeWidth=2.5;fontSize=13;fontFamily=Helvetica;fontColor=#134E4A;" vertex="1" parent="1">
      <mxGeometry x="960" y="255" width="190" height="95" as="geometry"/>
    </mxCell>

    <!-- END -->
    <mxCell id="node_end" value="&lt;b&gt;END&lt;/b&gt;" style="ellipse;whiteSpace=wrap;html=1;fillColor=#1E293B;strokeColor=#0F172A;fontSize=12;fontColor=#FFFFFF;fontFamily=Helvetica;" vertex="1" parent="1">
      <mxGeometry x="1230" y="277.5" width="80" height="50" as="geometry"/>
    </mxCell>

    <!-- Edges -->
    <mxCell id="e_start_router" style="edgeStyle=orthogonalEdgeStyle;rounded=1;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#1E293B;strokeWidth=2;" edge="1" parent="1" source="node_start" target="node_v_router">
      <mxGeometry relative="1" as="geometry"/>
    </mxCell>

    <mxCell id="e_r_retrieve" value="route = local" style="edgeStyle=orthogonalEdgeStyle;rounded=1;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#059669;strokeWidth=2;fontSize=11;fontStyle=1;fontColor=#065F46;" edge="1" parent="1" source="node_v_router" target="node_v_retrieve">
      <mxGeometry relative="1" as="geometry"/>
    </mxCell>

    <mxCell id="e_r_expert" value="route = expert" style="edgeStyle=orthogonalEdgeStyle;rounded=1;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#7C3AED;strokeWidth=2;fontSize=11;fontStyle=1;fontColor=#6D28D9;" edge="1" parent="1" source="node_v_router" target="node_v_expert">
      <mxGeometry relative="1" as="geometry"/>
    </mxCell>

    <mxCell id="e_r_repl" value="route = code" style="edgeStyle=orthogonalEdgeStyle;rounded=1;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#DB2777;strokeWidth=2;fontSize=11;fontStyle=1;fontColor=#BE185D;" edge="1" parent="1" source="node_v_router" target="node_v_repl">
      <mxGeometry relative="1" as="geometry"/>
    </mxCell>

    <mxCell id="e_retrieve_grade" style="edgeStyle=orthogonalEdgeStyle;rounded=1;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#059669;strokeWidth=2;" edge="1" parent="1" source="node_v_retrieve" target="node_v_grade">
      <mxGeometry relative="1" as="geometry"/>
    </mxCell>

    <mxCell id="e_grade_pass" value="grade = pass" style="edgeStyle=orthogonalEdgeStyle;rounded=1;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#059669;strokeWidth=2;fontSize=11;fontStyle=1;fontColor=#047857;" edge="1" parent="1" source="node_v_grade" target="node_v_generate">
      <mxGeometry relative="1" as="geometry"/>
    </mxCell>

    <mxCell id="e_grade_fail" value="grade = fail" style="edgeStyle=orthogonalEdgeStyle;rounded=1;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#D97706;strokeWidth=2;fontSize=11;fontStyle=1;fontColor=#C2410C;" edge="1" parent="1" source="node_v_grade" target="node_v_web">
      <mxGeometry relative="1" as="geometry"/>
    </mxCell>

    <mxCell id="e_web_gen" style="edgeStyle=orthogonalEdgeStyle;rounded=1;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#EA580C;strokeWidth=2;" edge="1" parent="1" source="node_v_web" target="node_v_generate">
      <mxGeometry relative="1" as="geometry"/>
    </mxCell>

    <mxCell id="e_expert_gen" style="edgeStyle=orthogonalEdgeStyle;rounded=1;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#7C3AED;strokeWidth=2;" edge="1" parent="1" source="node_v_expert" target="node_v_generate">
      <mxGeometry relative="1" as="geometry">
        <Array as="points">
          <mxPoint x="640" y="235"/>
          <mxPoint x="640" y="300"/>
        </Array>
      </mxGeometry>
    </mxCell>

    <mxCell id="e_repl_gen" style="edgeStyle=orthogonalEdgeStyle;rounded=1;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#DB2777;strokeWidth=2;" edge="1" parent="1" source="node_v_repl" target="node_v_generate">
      <mxGeometry relative="1" as="geometry">
        <Array as="points">
          <mxPoint x="900" y="505"/>
          <mxPoint x="900" y="320"/>
        </Array>
      </mxGeometry>
    </mxCell>

    <!-- Self-Correction Loop -->
    <mxCell id="e_gen_loop" value="hallucinated ∧ r &lt; 2" style="edgeStyle=orthogonalEdgeStyle;rounded=1;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#DC2626;strokeWidth=2.5;dashed=1;fontSize=11;fontStyle=1;fontColor=#B91C1C;" edge="1" parent="1" source="node_v_generate" target="node_v_generate">
      <mxGeometry relative="1" as="geometry">
        <Array as="points">
          <mxPoint x="1055" y="380"/>
          <mxPoint x="1120" y="380"/>
          <mxPoint x="1120" y="280"/>
        </Array>
      </mxGeometry>
    </mxCell>

    <!-- Terminal Edge -->
    <mxCell id="e_gen_end" value="grounded ∨ r ≥ 2" style="edgeStyle=orthogonalEdgeStyle;rounded=1;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#0D9488;strokeWidth=2.5;fontSize=11;fontStyle=1;fontColor=#115E59;" edge="1" parent="1" source="node_v_generate" target="node_end">
      <mxGeometry relative="1" as="geometry"/>
    </mxCell>

  </root>
</mxGraphModel>`;
}

// -----------------------------------------------------------------------------
// DIAGRAM 3: SciStudio Software Architecture (fig3_scistudio_software_architecture.drawio)
// -----------------------------------------------------------------------------
function buildFig3XML() {
  return `<mxGraphModel dx="1400" dy="850" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="1300" pageHeight="800" background="#FFFFFF" math="0" shadow="0">
  <root>
    <mxCell id="0"/>
    <mxCell id="1" parent="0"/>

    <!-- Container 1: Presentation Layer -->
    <mxCell id="c_pres" value="&lt;b&gt;Presentation Layer (Vue 3 + Vite SPA)&lt;/b&gt;" style="swimlane;whiteSpace=wrap;html=1;fillColor=#F8FAFC;strokeColor=#64748B;strokeWidth=1.5;startSize=26;fontSize=12;fontFamily=Helvetica;fontColor=#0F172A;" vertex="1" parent="1">
      <mxGeometry x="50" y="40" width="1200" height="110" as="geometry"/>
    </mxCell>
    <mxCell id="n_monaco" value="&lt;b&gt;Monaco Editor&lt;/b&gt;&lt;br&gt;&lt;font style=&quot;font-size: 10px;&quot;&gt;LaTeX / MD Syntax Sync&lt;/font&gt;" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#EFF6FF;strokeColor=#3B82F6;strokeWidth=1.5;fontSize=11;" vertex="1" parent="c_pres">
      <mxGeometry x="30" y="38" width="240" height="55" as="geometry"/>
    </mxCell>
    <mxCell id="n_pdfview" value="&lt;b&gt;PyMuPDF Viewer&lt;/b&gt;&lt;br&gt;&lt;font style=&quot;font-size: 10px;&quot;&gt;PDF Canvas Rendering&lt;/font&gt;" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#EFF6FF;strokeColor=#3B82F6;strokeWidth=1.5;fontSize=11;" vertex="1" parent="c_pres">
      <mxGeometry x="330" y="38" width="240" height="55" as="geometry"/>
    </mxCell>
    <mxCell id="n_cite" value="&lt;b&gt;Click-to-Verify Engine&lt;/b&gt;&lt;br&gt;&lt;font style=&quot;font-size: 10px;&quot;&gt;Bounding Box &amp;amp; Excerpt Tooltip&lt;/font&gt;" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#EFF6FF;strokeColor=#3B82F6;strokeWidth=1.5;fontSize=11;" vertex="1" parent="c_pres">
      <mxGeometry x="630" y="38" width="250" height="55" as="geometry"/>
    </mxCell>
    <mxCell id="n_wsclient" value="&lt;b&gt;WebSocket Stream Client&lt;/b&gt;&lt;br&gt;&lt;font style=&quot;font-size: 10px;&quot;&gt;Live Token &amp;amp; State Stream&lt;/font&gt;" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#EFF6FF;strokeColor=#3B82F6;strokeWidth=1.5;fontSize=11;" vertex="1" parent="c_pres">
      <mxGeometry x="930" y="38" width="240" height="55" as="geometry"/>
    </mxCell>

    <!-- Container 2: API Gateway & Service Layer -->
    <mxCell id="c_api" value="&lt;b&gt;API Gateway &amp;amp; Backend Services (FastAPI)&lt;/b&gt;" style="swimlane;whiteSpace=wrap;html=1;fillColor=#F8FAFC;strokeColor=#64748B;strokeWidth=1.5;startSize=26;fontSize=12;fontFamily=Helvetica;fontColor=#0F172A;" vertex="1" parent="1">
      <mxGeometry x="50" y="190" width="1200" height="110" as="geometry"/>
    </mxCell>
    <mxCell id="n_rest" value="&lt;b&gt;REST Endpoints&lt;/b&gt;&lt;br&gt;&lt;font style=&quot;font-size: 10px;&quot;&gt;/api/projects, /api/papers&lt;/font&gt;" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#EEF2FF;strokeColor=#6366F1;strokeWidth=1.5;fontSize=11;" vertex="1" parent="c_api">
      <mxGeometry x="30" y="38" width="240" height="55" as="geometry"/>
    </mxCell>
    <mxCell id="n_ws" value="&lt;b&gt;WebSocket Gateway&lt;/b&gt;&lt;br&gt;&lt;font style=&quot;font-size: 10px;&quot;&gt;/ws/chat Real-Time Channel&lt;/font&gt;" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#EEF2FF;strokeColor=#6366F1;strokeWidth=1.5;fontSize=11;" vertex="1" parent="c_api">
      <mxGeometry x="330" y="38" width="240" height="55" as="geometry"/>
    </mxCell>
    <mxCell id="n_auth" value="&lt;b&gt;Security &amp;amp; Auth&lt;/b&gt;&lt;br&gt;&lt;font style=&quot;font-size: 10px;&quot;&gt;JWT Bearer + Rate Limiting&lt;/font&gt;" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#EEF2FF;strokeColor=#6366F1;strokeWidth=1.5;fontSize=11;" vertex="1" parent="c_api">
      <mxGeometry x="630" y="38" width="250" height="55" as="geometry"/>
    </mxCell>
    <mxCell id="n_sync" value="&lt;b&gt;Citation Linker Service&lt;/b&gt;&lt;br&gt;&lt;font style=&quot;font-size: 10px;&quot;&gt;BibTeX + CrossRef Resolver&lt;/font&gt;" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#EEF2FF;strokeColor=#6366F1;strokeWidth=1.5;fontSize=11;" vertex="1" parent="c_api">
      <mxGeometry x="930" y="38" width="240" height="55" as="geometry"/>
    </mxCell>

    <!-- Container 3: LangGraph Agentic RAG Core -->
    <mxCell id="c_agent" value="&lt;b&gt;Core Agentic Engine (LangGraph State Graph)&lt;/b&gt;" style="swimlane;whiteSpace=wrap;html=1;fillColor=#F8FAFC;strokeColor=#64748B;strokeWidth=1.5;startSize=26;fontSize=12;fontFamily=Helvetica;fontColor=#0F172A;" vertex="1" parent="1">
      <mxGeometry x="50" y="340" width="1200" height="110" as="geometry"/>
    </mxCell>
    <mxCell id="n_core_router" value="&lt;b&gt;Intent Router&lt;/b&gt;&lt;br&gt;&lt;font style=&quot;font-size: 10px;&quot;&gt;Qwen-7B + Heuristics&lt;/font&gt;" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#ECFDF5;strokeColor=#10B981;strokeWidth=1.5;fontSize=11;" vertex="1" parent="c_agent">
      <mxGeometry x="30" y="38" width="240" height="55" as="geometry"/>
    </mxCell>
    <mxCell id="n_core_rrf" value="&lt;b&gt;Weighted RRF Engine&lt;/b&gt;&lt;br&gt;&lt;font style=&quot;font-size: 10px;&quot;&gt;Chroma + BM25 (w=0.7/0.3)&lt;/font&gt;" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#ECFDF5;strokeColor=#10B981;strokeWidth=1.5;fontSize=11;" vertex="1" parent="c_agent">
      <mxGeometry x="330" y="38" width="240" height="55" as="geometry"/>
    </mxCell>
    <mxCell id="n_core_grade" value="&lt;b&gt;Relevance &amp;amp; Fallback&lt;/b&gt;&lt;br&gt;&lt;font style=&quot;font-size: 10px;&quot;&gt;Token Overlap + DuckDuckGo&lt;/font&gt;" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#ECFDF5;strokeColor=#10B981;strokeWidth=1.5;fontSize=11;" vertex="1" parent="c_agent">
      <mxGeometry x="630" y="38" width="250" height="55" as="geometry"/>
    </mxCell>
    <mxCell id="n_core_llm" value="&lt;b&gt;Ollama Local LLM&lt;/b&gt;&lt;br&gt;&lt;font style=&quot;font-size: 10px;&quot;&gt;Qwen2.5-7B (Self-Correction)&lt;/font&gt;" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#ECFDF5;strokeColor=#10B981;strokeWidth=1.5;fontSize=11;" vertex="1" parent="c_agent">
      <mxGeometry x="930" y="38" width="240" height="55" as="geometry"/>
    </mxCell>

    <!-- Container 4: Persistence & Storage Layer -->
    <mxCell id="c_store" value="&lt;b&gt;Storage &amp;amp; Indexing Layer&lt;/b&gt;" style="swimlane;whiteSpace=wrap;html=1;fillColor=#F8FAFC;strokeColor=#64748B;strokeWidth=1.5;startSize=26;fontSize=12;fontFamily=Helvetica;fontColor=#0F172A;" vertex="1" parent="1">
      <mxGeometry x="50" y="490" width="1200" height="110" as="geometry"/>
    </mxCell>
    <mxCell id="n_chroma" value="&lt;b&gt;ChromaDB Store&lt;/b&gt;&lt;br&gt;&lt;font style=&quot;font-size: 10px;&quot;&gt;144,380 Document Embeddings&lt;/font&gt;" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#FFFBEB;strokeColor=#F59E0B;strokeWidth=1.5;fontSize=11;" vertex="1" parent="c_store">
      <mxGeometry x="30" y="38" width="240" height="55" as="geometry"/>
    </mxCell>
    <mxCell id="n_bm25" value="&lt;b&gt;BM25 Pickle Cache&lt;/b&gt;&lt;br&gt;&lt;font style=&quot;font-size: 10px;&quot;&gt;In-Memory Index (0.84s init)&lt;/font&gt;" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#FFFBEB;strokeColor=#F59E0B;strokeWidth=1.5;fontSize=11;" vertex="1" parent="c_store">
      <mxGeometry x="330" y="38" width="240" height="55" as="geometry"/>
    </mxCell>
    <mxCell id="n_sqlite" value="&lt;b&gt;SQLite Database&lt;/b&gt;&lt;br&gt;&lt;font style=&quot;font-size: 10px;&quot;&gt;Users, Projects, Chat Revisions&lt;/font&gt;" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#FFFBEB;strokeColor=#F59E0B;strokeWidth=1.5;fontSize=11;" vertex="1" parent="c_store">
      <mxGeometry x="630" y="38" width="250" height="55" as="geometry"/>
    </mxCell>
    <mxCell id="n_sandbox" value="&lt;b&gt;REPL Subprocess Jail&lt;/b&gt;&lt;br&gt;&lt;font style=&quot;font-size: 10px;&quot;&gt;Restricted Execution Environment&lt;/font&gt;" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#FFFBEB;strokeColor=#F59E0B;strokeWidth=1.5;fontSize=11;" vertex="1" parent="c_store">
      <mxGeometry x="930" y="38" width="240" height="55" as="geometry"/>
    </mxCell>

    <!-- Inter-layer Arrows -->
    <mxCell id="edge_l1_l2" style="edgeStyle=orthogonalEdgeStyle;rounded=1;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#64748B;strokeWidth=2;entryX=0.5;entryY=0;exitX=0.5;exitY=1;" edge="1" parent="1" source="c_pres" target="c_api">
      <mxGeometry relative="1" as="geometry"/>
    </mxCell>
    <mxCell id="edge_l2_l3" style="edgeStyle=orthogonalEdgeStyle;rounded=1;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#64748B;strokeWidth=2;entryX=0.5;entryY=0;exitX=0.5;exitY=1;" edge="1" parent="1" source="c_api" target="c_agent">
      <mxGeometry relative="1" as="geometry"/>
    </mxCell>
    <mxCell id="edge_l3_l4" style="edgeStyle=orthogonalEdgeStyle;rounded=1;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#64748B;strokeWidth=2;entryX=0.5;entryY=0;exitX=0.5;exitY=1;" edge="1" parent="1" source="c_agent" target="c_store">
      <mxGeometry relative="1" as="geometry"/>
    </mxCell>

  </root>
</mxGraphModel>`;
}

// -----------------------------------------------------------------------------
// Generation & URL Compression
// -----------------------------------------------------------------------------
const diagrams = [
  { filename: 'fig1_overall_architecture.drawio', xml: buildFig1XML(), title: 'Figure 1: Overall System Architecture' },
  { filename: 'fig2_langgraph_state_machine.drawio', xml: buildFig2XML(), title: 'Figure 2: LangGraph State Machine Graph' },
  { filename: 'fig3_scistudio_software_architecture.drawio', xml: buildFig3XML(), title: 'Figure 3: SciStudio Software Architecture' }
];

console.log('--- Generating Native Draw.io Diagrams ---');
const report = [];

diagrams.forEach(diag => {
  let xml = diag.xml;
  // Repair pass (per Draw.io skill)
  const diagramMatch = xml.match(/<mxfile[\s\S]*?<\/mxfile>|<mxGraphModel[\s\S]*?<\/mxGraphModel>/);
  if (diagramMatch && xml.trim() !== diagramMatch[0]) xml = diagramMatch[0];
  xml = xml.replace(/="([^"]*)"/g, (m, v) => {
    return '="' + v.replace(/</g, '&lt;').replace(/&(?!(?:amp|lt|gt|quot|apos|#[0-9]+|#x[0-9a-fA-F]+);)/g, '&amp;') + '"';
  });
  xml = xml.replace(/<mxCell id="([^"]+)" parent="\1"\s*\/>/g, '<mxCell id="$1" parent="0"/>');

  // Compute live browser edit URL
  const compressed = zlib.deflateRawSync(encodeURIComponent(xml)).toString('base64');
  const browserUrl = `https://app.diagrams.net/?grid=0&pv=0&border=10&edit=_blank#R${encodeURIComponent(compressed)}`;

  DIRS.forEach(dir => {
    const dest = path.join(dir, diag.filename);
    fs.writeFileSync(dest, xml, 'utf8');
    console.log(`Saved: ${dest}`);
  });

  report.push({
    title: diag.title,
    filename: diag.filename,
    url: browserUrl
  });
});

fs.writeFileSync(
  path.join(ROOT, 'manuscripts/DRAWIO_DIAGRAMS_LINKS.md'),
  `# Draw.io Diagrams - Interactive Web Links & Source Files

Generated on: ${new Date().toISOString()}

All diagrams below have been authored as native \`.drawio\` files according to the advisor's feedback and Springer/Elsevier publication standards. Click the web link to open and interactively edit each diagram directly in your web browser via draw.io (diagrams.net):

${report.map(r => `### ${r.title}
- **Local File:** \`${r.filename}\`
- **Interactive Browser Edit Link:** [Open in diagrams.net](${r.url})
`).join('\n')}
`,
  'utf8'
);

console.log('Saved interactive link report to manuscripts/DRAWIO_DIAGRAMS_LINKS.md');
