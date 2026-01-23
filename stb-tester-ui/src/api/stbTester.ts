/**
 * STB Tester Portal API Client
 * Connects to the same backend as the MCP server
 */

const API_BASE = '/api/v2';

// These would normally come from environment variables or config
const CONFIG = {
  portalUrl: 'https://ziggo.stb-tester.com',
  token: 'cBqdzRDwYbX1LI6cmskfsycAXNAIZPSs',
  defaultDevice: 'stb-tester-48b02d5b0ab7',
};

interface ApiResponse<T> {
  data?: T;
  error?: string;
}

async function apiRequest<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<ApiResponse<T>> {
  try {
    const response = await fetch(`${API_BASE}${endpoint}`, {
      ...options,
      headers: {
        'Authorization': `token ${CONFIG.token}`,
        'Content-Type': 'application/json',
        ...options.headers,
      },
    });

    if (!response.ok) {
      const errorText = await response.text();
      return { error: `HTTP ${response.status}: ${errorText}` };
    }

    // Handle binary responses (screenshots)
    const contentType = response.headers.get('content-type');
    if (contentType?.includes('image/')) {
      const blob = await response.blob();
      return { data: URL.createObjectURL(blob) as unknown as T };
    }

    const data = await response.json();
    return { data };
  } catch (err) {
    return { error: err instanceof Error ? err.message : 'Unknown error' };
  }
}

// ============ Device Management ============

export interface STBDevice {
  node_id: string;
  state: string;
  test_pack?: string;
  serial_number?: string;
  last_seen?: string;
}

export async function listDevices(): Promise<ApiResponse<STBDevice[]>> {
  const result = await apiRequest<{ nodes: STBDevice[] } | STBDevice[]>('/nodes');
  if (result.error) return { error: result.error };

  // Handle both array and object responses
  const nodes = Array.isArray(result.data) ? result.data : result.data?.nodes || [];
  return { data: nodes };
}

export async function getDeviceInfo(deviceId: string): Promise<ApiResponse<STBDevice>> {
  return apiRequest<STBDevice>(`/nodes/${deviceId}`);
}

// ============ Device Control ============

export async function getScreenshot(deviceId: string): Promise<ApiResponse<string>> {
  try {
    const response = await fetch(`${API_BASE}/nodes/${deviceId}/screenshot.png`, {
      headers: {
        'Authorization': `token ${CONFIG.token}`,
      },
    });

    if (!response.ok) {
      return { error: `Failed to get screenshot: ${response.status}` };
    }

    const blob = await response.blob();
    return { data: URL.createObjectURL(blob) };
  } catch (err) {
    return { error: err instanceof Error ? err.message : 'Unknown error' };
  }
}

export async function pressKey(deviceId: string, key: string): Promise<ApiResponse<{ status: string }>> {
  return apiRequest(`/nodes/${deviceId}/press`, {
    method: 'POST',
    body: JSON.stringify({ key }),
  });
}

// ============ Test Execution ============

export interface TestJob {
  job_uid: string;
  status: string;
  result?: string;
  failure_reason?: string;
  start_time?: string;
  end_time?: string;
  result_url?: string;
}

export async function runTest(
  nodeId: string,
  testPackRevision: string,
  testCases: string[]
): Promise<ApiResponse<TestJob>> {
  return apiRequest('/run_tests', {
    method: 'POST',
    body: JSON.stringify({
      node_id: nodeId,
      test_pack_revision: testPackRevision,
      test_cases: testCases,
    }),
  });
}

export async function getJobStatus(jobUid: string): Promise<ApiResponse<TestJob>> {
  return apiRequest(`/jobs/${jobUid}`);
}

export async function awaitJobCompletion(jobUid: string): Promise<ApiResponse<TestJob>> {
  return apiRequest(`/jobs/${jobUid}/await_completion`);
}

export async function cancelJob(jobUid: string): Promise<ApiResponse<{ job_uid: string }>> {
  return apiRequest(`/jobs${jobUid}/stop`, {
    method: 'POST',
  });
}

export async function listTestCases(testPackRevision: string): Promise<ApiResponse<string[]>> {
  return apiRequest(`/test_pack/${testPackRevision}/test_case_names`);
}

// ============ Test Results History ============

export interface TestResult {
  job_id: string;
  test_case: string;
  status: string;
  result: string;
  failure_reason?: string;
  start_time: string;
  end_time?: string;
  duration_seconds?: number;
  video_url?: string;
  node_id?: string;
}

export async function getTestHistory(
  limit = 50,
  filter?: { status?: string; node_id?: string }
): Promise<ApiResponse<TestResult[]>> {
  let endpoint = `/results?limit=${limit}`;
  if (filter?.status) endpoint += `&status=${filter.status}`;
  if (filter?.node_id) endpoint += `&node_id=${filter.node_id}`;

  return apiRequest<TestResult[]>(endpoint);
}

// ============ Video Recording ============

export async function getVideoUrl(deviceId: string): Promise<ApiResponse<string>> {
  // Get the most recent test result for this device which has a video
  const results = await getTestHistory(1, { node_id: deviceId });
  if (results.error) return { error: results.error };
  if (!results.data || results.data.length === 0) {
    return { error: 'No test results found' };
  }

  const videoUrl = results.data[0].video_url;
  if (!videoUrl) {
    return { error: 'No video available for this test' };
  }

  return { data: videoUrl };
}

// Start recording video on the device
export async function startRecording(deviceId: string): Promise<ApiResponse<{ recording_id: string }>> {
  return apiRequest(`/nodes/${deviceId}/recording/start`, {
    method: 'POST',
  });
}

// Stop recording and get video URL
export async function stopRecording(deviceId: string): Promise<ApiResponse<{ video_url: string }>> {
  return apiRequest(`/nodes/${deviceId}/recording/stop`, {
    method: 'POST',
  });
}

// Get live video stream URL (synchronous - just builds the URL)
export function getLiveStreamUrl(deviceId: string): string {
  // Use the proxy path to avoid CORS issues (Vite proxies /api/v2 to the portal)
  return `${API_BASE}/nodes/${deviceId}/stream.m3u8?token=${CONFIG.token}`;
}

// Get video URL from a specific job/test result
export async function getJobVideoUrl(jobUid: string): Promise<ApiResponse<string>> {
  const job = await getJobStatus(jobUid);
  if (job.error) return { error: job.error };

  // Video URL is typically at the result_url with /video.webm appended
  if (job.data?.result_url) {
    return { data: `${job.data.result_url}/video.webm` };
  }

  return { error: 'No video available for this job' };
}

// ============ Utility Functions ============

export function getDefaultDevice(): string {
  return CONFIG.defaultDevice;
}

export function getPortalUrl(): string {
  return CONFIG.portalUrl;
}

// Common remote control keys
export const REMOTE_KEYS = {
  // Navigation
  UP: 'KEY_UP',
  DOWN: 'KEY_DOWN',
  LEFT: 'KEY_LEFT',
  RIGHT: 'KEY_RIGHT',
  OK: 'KEY_OK',
  BACK: 'KEY_BACK',
  HOME: 'KEY_HOME',

  // EPG/Guide
  EPG: 'KEY_EPG',
  INFO: 'KEY_INFO',
  MENU: 'KEY_MENU',

  // Playback
  PLAY: 'KEY_PLAY',
  PAUSE: 'KEY_PAUSE',
  STOP: 'KEY_STOP',
  FAST_FORWARD: 'KEY_FASTFORWARD',
  REWIND: 'KEY_REWIND',

  // Numbers
  NUM_0: 'KEY_0',
  NUM_1: 'KEY_1',
  NUM_2: 'KEY_2',
  NUM_3: 'KEY_3',
  NUM_4: 'KEY_4',
  NUM_5: 'KEY_5',
  NUM_6: 'KEY_6',
  NUM_7: 'KEY_7',
  NUM_8: 'KEY_8',
  NUM_9: 'KEY_9',

  // Color buttons
  RED: 'KEY_RED',
  GREEN: 'KEY_GREEN',
  YELLOW: 'KEY_YELLOW',
  BLUE: 'KEY_BLUE',
} as const;
