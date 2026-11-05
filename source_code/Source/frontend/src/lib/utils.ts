/**
 * Utility helper functions for UI formatting and Agent node labels
 */

export function formatRelativeTime(dateString?: string | null): string {
  if (!dateString) return '';
  const date = new Date(dateString);
  if (isNaN(date.getTime())) return '';

  const now = new Date();
  const diffInSeconds = Math.floor((now.getTime() - date.getTime()) / 1000);

  if (diffInSeconds < 60) return 'Just now';
  const diffInMinutes = Math.floor(diffInSeconds / 60);
  if (diffInMinutes < 60) return `${diffInMinutes}m ago`;
  const diffInHours = Math.floor(diffInMinutes / 60);
  if (diffInHours < 24) return `${diffInHours}h ago`;
  const diffInDays = Math.floor(diffInHours / 24);
  if (diffInDays === 1) return 'Yesterday';
  if (diffInDays < 7) return `${diffInDays}d ago`;

  return date.toLocaleDateString();
}

export function getNodeInfo(nodeName: string): { label: string; cssClass: string } {
  const cleanName = (nodeName || '').toLowerCase().trim();

  switch (cleanName) {
    case 'router':
    case 'router_node':
      return { label: 'Routing Query', cssClass: 'node-badge node-router' };
    case 'retrieve':
    case 'retrieve_node':
      return { label: 'Retrieving Docs', cssClass: 'node-badge node-retrieve' };
    case 'grade':
    case 'grade_documents':
    case 'grader_node':
      return { label: 'Grading Relevance', cssClass: 'node-badge node-grade' };
    case 'generate':
    case 'generator_node':
      return { label: 'Synthesizing Answer', cssClass: 'node-badge node-generate' };
    case 'web_search':
    case 'web_search_node':
    case 'tavily_search':
      return { label: 'Searching Web', cssClass: 'node-badge node-web_search' };
    case 'python_repl':
    case 'python_code_interpreter':
      return { label: 'Executing Python', cssClass: 'node-badge node-python_repl' };
    case 'export_workspace':
    case 'export_node':
    case 'export':
      return { label: 'Exporting Workspace', cssClass: 'node-badge node-export' };
    default:
      return {
        label: nodeName.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase()),
        cssClass: 'node-badge node-default',
      };
  }
}
