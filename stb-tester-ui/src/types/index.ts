export interface TestCase {
  id: string;
  name: string;
  description: string;
  status: 'draft' | 'ready' | 'running' | 'passed' | 'failed';
  createdAt: Date;
  updatedAt: Date;
  code?: string;
  userStory?: string;
  scenarios?: Scenario[];
}

export interface Scenario {
  id: string;
  name: string;
  given: string;
  when: string;
  then: string[];
}

export interface TestResult {
  id: string;
  testCaseId: string;
  testCaseName: string;
  status: 'passed' | 'failed' | 'error' | 'skipped';
  duration: number;
  startedAt: Date;
  completedAt: Date;
  logs?: string;
  screenshot?: string;
  videoUrl?: string;
  errorMessage?: string;
}

export interface MCPServer {
  id: string;
  name: string;
  command: string;
  args: string[];
  env: Record<string, string>;
  status: 'connected' | 'disconnected' | 'error';
}

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  testCase?: TestCase;
}

export interface AppState {
  activeTab: 'chat' | 'testcases' | 'results' | 'mcp';
  testCases: TestCase[];
  results: TestResult[];
  mcpServers: MCPServer[];
  chatMessages: ChatMessage[];
  isThinking: boolean;
  currentModel: string;
}
