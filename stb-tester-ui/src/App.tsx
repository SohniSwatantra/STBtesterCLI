import { useState, useEffect, useRef } from 'react';
import * as api from './api/stbTester';

// Types
interface TestCase {
  id: string;
  name: string;
  description: string;
  status: 'draft' | 'ready' | 'running' | 'passed' | 'failed';
}

interface TestResult {
  id: string;
  testCaseName: string;
  status: 'passed' | 'failed' | 'error';
  duration: number;
  completedAt: Date;
  errorMessage?: string;
  videoUrl?: string;
}

interface ActivityLogEntry {
  id: string;
  type: 'tool' | 'result' | 'info' | 'error';
  tool?: string;
  command?: string;
  output?: string[];
  status: 'running' | 'done' | 'error';
  timestamp: Date;
  duration?: number;
}

interface RecordedFrame {
  screenshot: string;
  timestamp: number;
  label?: string;
}

interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  screenshot?: string;
  activityLog?: ActivityLogEntry[];
  videoUrl?: string;
  recordedFrames?: RecordedFrame[];
}

interface MCPTool {
  name: string;
  description: string;
  category: 'device' | 'control' | 'verify' | 'navigate';
  parameters: { name: string; type: string; required: boolean; description: string }[];
}

const MCP_TOOLS: MCPTool[] = [
  // Device management tools
  { name: 'stb_list_devices', description: 'List all available STB Tester devices', category: 'device', parameters: [] },
  { name: 'stb_connect_device', description: 'Connect to a specific STB device by ID', category: 'device', parameters: [
    { name: 'device_id', type: 'string', required: true, description: 'The device ID to connect to' }
  ]},
  { name: 'stb_device_info', description: 'Get detailed information about connected device', category: 'device', parameters: [
    { name: 'device_id', type: 'string', required: false, description: 'Device ID (uses default if not specified)' }
  ]},
  // Control tools
  { name: 'stb_press', description: 'Press a remote control key', category: 'control', parameters: [
    { name: 'key', type: 'string', required: true, description: 'Key to press (e.g., KEY_OK, KEY_UP)' }
  ]},
  { name: 'stb_press_and_wait', description: 'Press key and wait for screen to stabilize', category: 'control', parameters: [
    { name: 'key', type: 'string', required: true, description: 'Key to press' },
    { name: 'stable_secs', type: 'number', required: false, description: 'Seconds to wait for stability' }
  ]},
  { name: 'stb_press_until_match', description: 'Press key repeatedly until image is found', category: 'control', parameters: [
    { name: 'key', type: 'string', required: true, description: 'Key to press' },
    { name: 'image', type: 'string', required: true, description: 'Reference image path' },
    { name: 'max_presses', type: 'number', required: false, description: 'Maximum number of presses' }
  ]},
  { name: 'stb_type_text', description: 'Type text using on-screen keyboard', category: 'control', parameters: [
    { name: 'text', type: 'string', required: true, description: 'Text to type' }
  ]},
  // Verify tools
  { name: 'stb_screenshot', description: 'Capture current screen frame', category: 'verify', parameters: [] },
  { name: 'stb_match', description: 'Check if reference image is visible on screen', category: 'verify', parameters: [
    { name: 'image', type: 'string', required: true, description: 'Reference image path' },
    { name: 'region', type: 'object', required: false, description: 'Screen region to search' }
  ]},
  { name: 'stb_wait_for_match', description: 'Wait for reference image to appear', category: 'verify', parameters: [
    { name: 'image', type: 'string', required: true, description: 'Reference image path' },
    { name: 'timeout_secs', type: 'number', required: false, description: 'Timeout in seconds' }
  ]},
  { name: 'stb_wait_for_motion', description: 'Wait for video motion (verify playback)', category: 'verify', parameters: [
    { name: 'timeout_secs', type: 'number', required: false, description: 'Timeout in seconds' },
    { name: 'region', type: 'object', required: false, description: 'Screen region to monitor' }
  ]},
  { name: 'stb_ocr', description: 'Read text from screen using OCR', category: 'verify', parameters: [
    { name: 'region', type: 'object', required: false, description: 'Screen region to read' },
    { name: 'mode', type: 'string', required: false, description: 'OCR mode (PAGE, LINE, etc.)' }
  ]},
  { name: 'stb_get_text', description: 'Get all visible text from current screen', category: 'verify', parameters: [] },
  // Navigate tools
  { name: 'stb_navigate_menu', description: 'Navigate through menu to find target', category: 'navigate', parameters: [
    { name: 'target', type: 'string', required: true, description: 'Target menu item text or image' },
    { name: 'direction', type: 'string', required: false, description: 'Navigation direction (down, right)' }
  ]},
  { name: 'stb_navigate_to', description: 'Navigate to a specific screen or state', category: 'navigate', parameters: [
    { name: 'destination', type: 'string', required: true, description: 'Destination screen name' }
  ]},
  { name: 'stb_go_home', description: 'Navigate to home screen', category: 'navigate', parameters: [] },
  { name: 'stb_run_test', description: 'Run a test script on the device', category: 'device', parameters: [
    { name: 'test_file', type: 'string', required: true, description: 'Test file path' },
    { name: 'args', type: 'object', required: false, description: 'Test arguments' }
  ]},
];

function App() {
  const [activeTab, setActiveTab] = useState<'chat' | 'testcases' | 'results' | 'devices' | 'mcp'>('chat');
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const [isThinking, setIsThinking] = useState(false);
  const [devices, setDevices] = useState<api.STBDevice[]>([]);
  const [connectedDevice, setConnectedDevice] = useState<string>(api.getDefaultDevice());
  const [screenshot, setScreenshot] = useState<string | null>(null);
  const [results] = useState<TestResult[]>([]);
  const [testCases] = useState<TestCase[]>([
    { id: '1', name: 'Open EPG Guide', description: 'Verify EPG opens from live TV', status: 'ready' },
    { id: '2', name: 'Navigate Channel List', description: 'Test channel navigation in EPG', status: 'passed' },
    { id: '3', name: 'Ziggo Menu Navigation', description: 'Navigate to Movies & Series', status: 'failed' },
  ]);
  const [currentActivityLog, setCurrentActivityLog] = useState<ActivityLogEntry[]>([]);
  const [availableTests, setAvailableTests] = useState<string[]>([]);
  const [runningTestId, setRunningTestId] = useState<string | null>(null);
  const [runningJob, setRunningJob] = useState<{ jobUid: string; testCase: string } | null>(null);
  const [showTestListRequest, setShowTestListRequest] = useState(0);
  const [darkMode, setDarkMode] = useState(() => {
    // Check localStorage or system preference
    const saved = localStorage.getItem('darkMode');
    if (saved !== null) return saved === 'true';
    return window.matchMedia('(prefers-color-scheme: dark)').matches;
  });
  const recordedFramesRef = useRef<RecordedFrame[]>([]);
  const recordingStartTimeRef = useRef<number>(Date.now());

  // Apply dark mode class to document
  useEffect(() => {
    if (darkMode) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
    localStorage.setItem('darkMode', String(darkMode));
  }, [darkMode]);

  // Helper to record a frame during test execution
  const recordFrame = (screenshotData: string, label?: string) => {
    const frame: RecordedFrame = {
      screenshot: screenshotData,
      timestamp: Date.now() - recordingStartTimeRef.current,
      label,
    };
    recordedFramesRef.current.push(frame);
  };

  // Helper to add activity log entry
  const addActivity = (entry: Omit<ActivityLogEntry, 'id' | 'timestamp'>) => {
    const newEntry: ActivityLogEntry = {
      ...entry,
      id: `activity-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      timestamp: new Date(),
    };
    setCurrentActivityLog(prev => [...prev, newEntry]);
    return newEntry.id;
  };

  // Helper to update activity status
  const updateActivity = (id: string, updates: Partial<ActivityLogEntry>) => {
    setCurrentActivityLog(prev => prev.map(entry =>
      entry.id === id ? { ...entry, ...updates } : entry
    ));
  };

  // Load devices on mount
  useEffect(() => {
    loadDevices();
  }, []);

  async function loadDevices() {
    const result = await api.listDevices();
    if (result.data) {
      setDevices(result.data);
    }
  }

  async function takeScreenshot() {
    if (!connectedDevice) return;
    const result = await api.getScreenshot(connectedDevice);
    if (result.data) {
      setScreenshot(result.data);
    }
  }

  async function sendKey(key: string) {
    if (!connectedDevice) return;
    await api.pressKey(connectedDevice, key);
    // Take screenshot after key press
    setTimeout(takeScreenshot, 500);
  }

  // Helper to execute a tool with activity logging
  async function executeWithLog(
    tool: string,
    command: string,
    action: () => Promise<{ output?: string[]; error?: string; screenshot?: string }>,
    frameLabel?: string
  ): Promise<{ success: boolean; output?: string[] }> {
    const startTime = Date.now();
    const activityId = addActivity({
      type: 'tool',
      tool,
      command,
      status: 'running',
    });

    try {
      const result = await action();
      const duration = Date.now() - startTime;

      // Record frame if screenshot was captured
      if (result.screenshot) {
        recordFrame(result.screenshot, frameLabel || tool);
      }

      if (result.error) {
        updateActivity(activityId, {
          status: 'error',
          output: [result.error],
          duration,
        });
        return { success: false, output: [result.error] };
      }

      updateActivity(activityId, {
        status: 'done',
        output: result.output,
        duration,
      });
      return { success: true, output: result.output };
    } catch (err) {
      const duration = Date.now() - startTime;
      const errorMsg = err instanceof Error ? err.message : 'Unknown error';
      updateActivity(activityId, {
        status: 'error',
        output: [errorMsg],
        duration,
      });
      return { success: false, output: [errorMsg] };
    }
  }

  // AI-like test generation and execution with activity logging
  async function executeAdHocTest(description: string): Promise<{ success: boolean; error?: string; videoUrl?: string }> {
    const lower = description.toLowerCase();

    try {
      // Start video recording
      await executeWithLog('stb_start_recording', `api.startRecording("${connectedDevice}")`, async () => {
        const result = await api.startRecording(connectedDevice);
        if (!result.error) {
          return { output: ['Recording started'] };
        }
        return { output: ['Recording not available - using screenshots'] };
      }, 'Start Recording');

      // Take initial screenshot
      await executeWithLog('stb_screenshot', `api.getScreenshot("${connectedDevice}")`, async () => {
        const result = await api.getScreenshot(connectedDevice);
        if (result.data) setScreenshot(result.data);
        return {
          output: result.data ? ['Screenshot captured successfully'] : ['Failed to capture screenshot'],
          screenshot: result.data || undefined
        };
      }, 'Initial');

      // Determine what actions to perform based on the description
      if (lower.includes('epg') || lower.includes('guide') || lower.includes('tv guide')) {
        await executeWithLog('stb_press', `api.pressKey("${connectedDevice}", "KEY_EPG")`, async () => {
          await api.pressKey(connectedDevice, 'KEY_EPG');
          return { output: ['Key pressed: KEY_EPG'] };
        });
        await new Promise(r => setTimeout(r, 2000));

        await executeWithLog('stb_screenshot', `api.getScreenshot("${connectedDevice}")`, async () => {
          const result = await api.getScreenshot(connectedDevice);
          if (result.data) setScreenshot(result.data);
          return { output: ['EPG screen captured'], screenshot: result.data || undefined };
        }, 'EPG Open');

      } else if (lower.includes('menu') || lower.includes('main menu')) {
        await executeWithLog('stb_press', `api.pressKey("${connectedDevice}", "KEY_MENU")`, async () => {
          await api.pressKey(connectedDevice, 'KEY_MENU');
          return { output: ['Key pressed: KEY_MENU'] };
        });
        await new Promise(r => setTimeout(r, 2000));

        await executeWithLog('stb_screenshot', `api.getScreenshot("${connectedDevice}")`, async () => {
          const result = await api.getScreenshot(connectedDevice);
          if (result.data) setScreenshot(result.data);
          return { output: ['Menu screen captured'], screenshot: result.data || undefined };
        }, 'Menu Open');

      } else if (lower.includes('home')) {
        await executeWithLog('stb_press', `api.pressKey("${connectedDevice}", "KEY_HOME")`, async () => {
          await api.pressKey(connectedDevice, 'KEY_HOME');
          return { output: ['Key pressed: KEY_HOME'] };
        });
        await new Promise(r => setTimeout(r, 2000));

        await executeWithLog('stb_screenshot', `api.getScreenshot("${connectedDevice}")`, async () => {
          const result = await api.getScreenshot(connectedDevice);
          if (result.data) setScreenshot(result.data);
          return { output: ['Home screen captured'], screenshot: result.data || undefined };
        }, 'Home Screen');

      } else if (lower.includes('channel') || lower.includes('navigate') || lower.includes('scroll')) {
        for (let i = 0; i < 3; i++) {
          await executeWithLog('stb_press', `api.pressKey("${connectedDevice}", "KEY_DOWN")`, async () => {
            await api.pressKey(connectedDevice, 'KEY_DOWN');
            const result = await api.getScreenshot(connectedDevice);
            if (result.data) setScreenshot(result.data);
            return { output: [`Key pressed: KEY_DOWN (${i + 1}/3)`], screenshot: result.data || undefined };
          }, `Navigate ${i + 1}`);
          await new Promise(r => setTimeout(r, 500));
        }

        await executeWithLog('stb_press', `api.pressKey("${connectedDevice}", "KEY_OK")`, async () => {
          await api.pressKey(connectedDevice, 'KEY_OK');
          return { output: ['Key pressed: KEY_OK - Channel selected'] };
        });
        await new Promise(r => setTimeout(r, 2000));

        await executeWithLog('stb_screenshot', `api.getScreenshot("${connectedDevice}")`, async () => {
          const result = await api.getScreenshot(connectedDevice);
          if (result.data) setScreenshot(result.data);
          return { output: ['Channel screen captured'], screenshot: result.data || undefined };
        }, 'Channel Selected');

      } else if (lower.includes('play') || lower.includes('video') || lower.includes('playback')) {
        await executeWithLog('stb_press', `api.pressKey("${connectedDevice}", "KEY_PLAY")`, async () => {
          await api.pressKey(connectedDevice, 'KEY_PLAY');
          return { output: ['Key pressed: KEY_PLAY'] };
        });
        await new Promise(r => setTimeout(r, 2000));

        await executeWithLog('stb_screenshot', `api.getScreenshot("${connectedDevice}")`, async () => {
          const result = await api.getScreenshot(connectedDevice);
          if (result.data) setScreenshot(result.data);
          return { output: ['Playback screen captured'], screenshot: result.data || undefined };
        }, 'Playback');

      } else {
        // Default: simple navigation test
        await executeWithLog('stb_press', `api.pressKey("${connectedDevice}", "KEY_DOWN")`, async () => {
          await api.pressKey(connectedDevice, 'KEY_DOWN');
          const result = await api.getScreenshot(connectedDevice);
          if (result.data) setScreenshot(result.data);
          return { output: ['Key pressed: KEY_DOWN'], screenshot: result.data || undefined };
        }, 'Down');
        await new Promise(r => setTimeout(r, 500));

        await executeWithLog('stb_press', `api.pressKey("${connectedDevice}", "KEY_RIGHT")`, async () => {
          await api.pressKey(connectedDevice, 'KEY_RIGHT');
          const result = await api.getScreenshot(connectedDevice);
          if (result.data) setScreenshot(result.data);
          return { output: ['Key pressed: KEY_RIGHT'], screenshot: result.data || undefined };
        }, 'Right');
        await new Promise(r => setTimeout(r, 500));

        await executeWithLog('stb_press', `api.pressKey("${connectedDevice}", "KEY_OK")`, async () => {
          await api.pressKey(connectedDevice, 'KEY_OK');
          const result = await api.getScreenshot(connectedDevice);
          if (result.data) setScreenshot(result.data);
          return { output: ['Key pressed: KEY_OK'], screenshot: result.data || undefined };
        }, 'Select');
        await new Promise(r => setTimeout(r, 1500));

        await executeWithLog('stb_screenshot', `api.getScreenshot("${connectedDevice}")`, async () => {
          const result = await api.getScreenshot(connectedDevice);
          if (result.data) setScreenshot(result.data);
          return { output: ['Screenshot captured'], screenshot: result.data || undefined };
        }, 'Result');

        await executeWithLog('stb_press', `api.pressKey("${connectedDevice}", "KEY_BACK")`, async () => {
          await api.pressKey(connectedDevice, 'KEY_BACK');
          const result = await api.getScreenshot(connectedDevice);
          if (result.data) setScreenshot(result.data);
          return { output: ['Key pressed: KEY_BACK - Returned to previous screen'], screenshot: result.data || undefined };
        }, 'Back');
        await new Promise(r => setTimeout(r, 1000));
      }

      // Stop recording and get video URL
      let videoUrl: string | undefined;
      await executeWithLog('stb_stop_recording', `api.stopRecording("${connectedDevice}")`, async () => {
        const result = await api.stopRecording(connectedDevice);
        if (result.data?.video_url) {
          videoUrl = result.data.video_url;
          return { output: [`Recording stopped - Video URL: ${videoUrl}`] };
        }
        return { output: ['Recording stopped - No video URL returned'] };
      }, 'Stop Recording');

      return { success: true, videoUrl };
    } catch (err) {
      // Try to stop recording even on error
      try {
        await api.stopRecording(connectedDevice);
      } catch {
        // Ignore stop recording errors
      }
      return { success: false, error: err instanceof Error ? err.message : 'Unknown error' };
    }
  }

  async function handleSendMessage() {
    if (!input.trim() || isThinking) return;

    // Clear activity log and recorded frames for new command
    setCurrentActivityLog([]);
    recordedFramesRef.current = [];
    recordingStartTimeRef.current = Date.now();

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      role: 'user',
      content: input,
      timestamp: new Date(),
    };
    setChatMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsThinking(true);

    // Process command - AI-like understanding
    const lower = input.toLowerCase();

    if (lower.includes('screenshot') || lower.includes('show screen') || lower.includes('what\'s on')) {
      await executeWithLog('stb_screenshot', `api.getScreenshot("${connectedDevice}")`, async () => {
        const result = await api.getScreenshot(connectedDevice);
        if (result.data) setScreenshot(result.data);
        return { output: result.data ? ['Screenshot captured'] : ['Failed'], error: result.error, screenshot: result.data || undefined };
      }, 'Screenshot');

      // Get final activity log and frames
      const finalLog = [...currentActivityLog];
      const finalFrames = [...recordedFramesRef.current];
      const screenshotResult = await api.getScreenshot(connectedDevice);

      const response: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: screenshotResult.data ? 'Here\'s the current screen:' : `Error: ${screenshotResult.error}`,
        timestamp: new Date(),
        screenshot: screenshotResult.data || undefined,
        activityLog: finalLog,
        recordedFrames: finalFrames.length > 0 ? finalFrames : undefined,
      };
      setChatMessages(prev => [...prev, response]);
    } else if (lower.includes('list') && (lower.includes('test') || lower.includes('testcase'))) {
      // List all available test cases from the portal - MUST come before "run test" check
      await executeWithLog('stb_list_test_cases', `api.listTestCases("HEAD")`, async () => {
        const result = await api.listTestCases('HEAD');
        if (result.data) {
          setAvailableTests(result.data);
          return { output: [`Found ${result.data.length} test cases`] };
        }
        return { error: result.error };
      });

      const finalLog = [...currentActivityLog];
      const result = await api.listTestCases('HEAD');

      if (result.data && result.data.length > 0) {
        setAvailableTests(result.data);
        // Trigger the test list modal to show
        setShowTestListRequest(prev => prev + 1);
        const response: ChatMessage = {
          id: (Date.now() + 1).toString(),
          role: 'assistant',
          content: `**Found ${result.data.length} Test Cases**\n\nClick "Run" to execute any test:`,
          timestamp: new Date(),
          activityLog: finalLog,
        };
        setChatMessages(prev => [...prev, response]);
      } else {
        const response: ChatMessage = {
          id: (Date.now() + 1).toString(),
          role: 'assistant',
          content: `**Error:** ${result.error || 'No test cases found'}`,
          timestamp: new Date(),
          activityLog: finalLog,
        };
        setChatMessages(prev => [...prev, response]);
      }
    } else if ((lower.includes('run') || lower.includes('test') || lower.includes('verify') || lower.includes('check')) && !lower.includes('list')) {
      // Run a REAL test through the STB Tester portal API
      const startTime = Date.now();

      // Step 1: Get available test cases
      const listActivityId = addActivity({
        type: 'tool',
        tool: 'stb_list_test_cases',
        command: 'api.listTestCases("HEAD")',
        status: 'running',
      });

      const testPackResult = await api.listTestCases('HEAD');

      if (testPackResult.error || !testPackResult.data || testPackResult.data.length === 0) {
        updateActivity(listActivityId, {
          status: 'error',
          output: [testPackResult.error || 'No test cases found in test pack'],
          duration: Date.now() - startTime,
        });

        const finalLog = [...currentActivityLog];
        const response: ChatMessage = {
          id: (Date.now() + 1).toString(),
          role: 'assistant',
          content: `**Could not list test cases:** ${testPackResult.error || 'No test cases found'}\n\nMake sure the test pack has test cases available.`,
          timestamp: new Date(),
          activityLog: finalLog,
        };
        setChatMessages(prev => [...prev, response]);
      } else {
        updateActivity(listActivityId, {
          status: 'done',
          output: [`Found ${testPackResult.data.length} test cases`],
          duration: Date.now() - startTime,
        });

        // Find a matching test case based on user input, or use first one
        let testCase = testPackResult.data[0];
        for (const tc of testPackResult.data) {
          const tcLower = tc.toLowerCase();
          if (lower.includes('epg') && tcLower.includes('epg')) { testCase = tc; break; }
          if (lower.includes('home') && tcLower.includes('home')) { testCase = tc; break; }
          if (lower.includes('channel') && tcLower.includes('channel')) { testCase = tc; break; }
          if (lower.includes('live') && tcLower.includes('live')) { testCase = tc; break; }
          if (lower.includes('sanity') && tcLower.includes('sanity')) { testCase = tc; break; }
        }

        // Step 2: Run the test
        const runStartTime = Date.now();
        const runActivityId = addActivity({
          type: 'tool',
          tool: 'stb_run_test',
          command: `api.runTest("${connectedDevice}", "HEAD", ["${testCase}"])`,
          status: 'running',
        });

        const runResult = await api.runTest(connectedDevice, 'HEAD', [testCase]);

        if (runResult.error || !runResult.data?.job_uid) {
          updateActivity(runActivityId, {
            status: 'error',
            output: [runResult.error || 'Failed to start test job'],
            duration: Date.now() - runStartTime,
          });

          const finalLog = [...currentActivityLog];
          const response: ChatMessage = {
            id: (Date.now() + 1).toString(),
            role: 'assistant',
            content: `**Failed to start test:** ${runResult.error || 'Unknown error'}`,
            timestamp: new Date(),
            activityLog: finalLog,
          };
          setChatMessages(prev => [...prev, response]);
        } else {
          const jobUid = runResult.data.job_uid;
          updateActivity(runActivityId, {
            status: 'done',
            output: [`Job started: ${jobUid}`],
            duration: Date.now() - runStartTime,
          });

          // Step 3: Wait for completion
          const awaitStartTime = Date.now();
          const awaitActivityId = addActivity({
            type: 'tool',
            tool: 'stb_await_completion',
            command: `api.awaitJobCompletion("${jobUid}")`,
            status: 'running',
          });

          const completionResult = await api.awaitJobCompletion(jobUid);

          if (completionResult.error) {
            updateActivity(awaitActivityId, {
              status: 'error',
              output: [completionResult.error],
              duration: Date.now() - awaitStartTime,
            });
          } else {
            const result = completionResult.data?.result || 'unknown';
            const resultUrl = completionResult.data?.result_url || '';

            updateActivity(awaitActivityId, {
              status: 'done',
              output: [
                `Result: ${result}`,
                `Video URL: ${resultUrl}`,
              ],
              duration: Date.now() - awaitStartTime,
            });
          }

          // Get final screenshot
          const finalScreenshot = await api.getScreenshot(connectedDevice);
          if (finalScreenshot.data) setScreenshot(finalScreenshot.data);

          const finalLog = [...currentActivityLog];
          const jobResult = completionResult.data;
          const triageUrl = jobResult?.result_url?.replace('/api/v2/results/', '/app/#/result/') || '';

          const response: ChatMessage = {
            id: (Date.now() + 1).toString(),
            role: 'assistant',
            content: `**Real Test Completed!**\n\n**Test Case:** ${testCase}\n**Result:** ${jobResult?.result || 'unknown'}\n${jobResult?.failure_reason ? `**Failure:** ${jobResult.failure_reason}\n` : ''}\n**📹 Video URL (paste in browser):**\n${triageUrl}\n\n**API Result URL:**\n${jobResult?.result_url || 'N/A'}`,
            timestamp: new Date(),
            screenshot: finalScreenshot.data || undefined,
            activityLog: finalLog,
          };
          setChatMessages(prev => [...prev, response]);
        }
      }
    } else if (lower.includes('press')) {
      // Extract key from message
      const keyMatch = lower.match(/press\s+(\w+)/i);
      const key = keyMatch ? `KEY_${keyMatch[1].toUpperCase()}` : 'KEY_OK';

      await executeWithLog('stb_press', `api.pressKey("${connectedDevice}", "${key}")`, async () => {
        await api.pressKey(connectedDevice, key);
        return { output: [`Key pressed: ${key}`] };
      });

      await new Promise(r => setTimeout(r, 500));

      await executeWithLog('stb_screenshot', `api.getScreenshot("${connectedDevice}")`, async () => {
        const result = await api.getScreenshot(connectedDevice);
        if (result.data) setScreenshot(result.data);
        return { output: ['Screenshot captured after key press'] };
      });

      const finalLog = [...currentActivityLog];
      const screenshotResult = await api.getScreenshot(connectedDevice);

      const response: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: `Pressed ${key}. Here's the result:`,
        timestamp: new Date(),
        screenshot: screenshotResult.data || undefined,
        activityLog: finalLog,
      };
      setChatMessages(prev => [...prev, response]);
    } else if (lower.includes('devices') || lower.includes('list device')) {
      await executeWithLog('stb_list_devices', `api.listDevices()`, async () => {
        const result = await api.listDevices();
        if (result.data) {
          setDevices(result.data);
          return { output: result.data.map(d => `${d.node_id} (${d.state})`) };
        }
        return { error: result.error };
      });

      const finalLog = [...currentActivityLog];
      const result = await api.listDevices();

      const response: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: result.data
          ? `Found ${result.data.length} devices:\n\n${result.data.map(d => `• **${d.node_id}**\n  State: ${d.state}`).join('\n\n')}`
          : `Error: ${result.error}`,
        timestamp: new Date(),
        activityLog: finalLog,
      };
      setChatMessages(prev => [...prev, response]);
    } else if (lower.includes('navigate') || lower.includes('go to')) {
      // Handle navigation commands
      const keys: string[] = [];
      if (lower.includes('menu')) keys.push('KEY_MENU');
      if (lower.includes('home')) keys.push('KEY_HOME');
      if (lower.includes('epg') || lower.includes('guide')) keys.push('KEY_EPG');
      if (lower.includes('up')) keys.push('KEY_UP');
      if (lower.includes('down')) keys.push('KEY_DOWN');
      if (lower.includes('left')) keys.push('KEY_LEFT');
      if (lower.includes('right')) keys.push('KEY_RIGHT');

      if (keys.length > 0) {
        for (const key of keys) {
          await executeWithLog('stb_press', `api.pressKey("${connectedDevice}", "${key}")`, async () => {
            await api.pressKey(connectedDevice, key);
            return { output: [`Key pressed: ${key}`] };
          });
          await new Promise(r => setTimeout(r, 500));
        }

        await executeWithLog('stb_screenshot', `api.getScreenshot("${connectedDevice}")`, async () => {
          const result = await api.getScreenshot(connectedDevice);
          if (result.data) setScreenshot(result.data);
          return { output: ['Navigation screenshot captured'] };
        });

        const finalLog = [...currentActivityLog];
        const screenshotResult = await api.getScreenshot(connectedDevice);

        const response: ChatMessage = {
          id: (Date.now() + 1).toString(),
          role: 'assistant',
          content: `Navigation complete. Pressed: ${keys.join(' → ')}\n\nHere's the result:`,
          timestamp: new Date(),
          screenshot: screenshotResult.data || undefined,
          activityLog: finalLog,
        };
        setChatMessages(prev => [...prev, response]);
      }
    } else if (lower.includes('help') || lower === 'hi' || lower === 'hello') {
      const response: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: `Hi! I'm your STB Tester assistant. Connected to: **${connectedDevice}**\n\n**Just tell me what you want to test!** For example:\n\n**Test Commands** (I'll create and run them instantly!)\n• "Run a simple test"\n• "Test the EPG guide"\n• "Verify the menu opens"\n• "Check channel navigation"\n• "Test video playback"\n\n**Device Control**\n• "Take a screenshot"\n• "Press Menu" / "Press OK"\n• "Navigate down 3 times"\n\n**Device Management**\n• "List devices"\n• "Show device info"\n\n**Tip:** Just describe what you want to test in plain English and I'll figure out the rest!`,
        timestamp: new Date(),
      };
      setChatMessages(prev => [...prev, response]);
    } else {
      // For any other input, try to run it as a test!
      const result = await executeAdHocTest(input);
      const finalScreenshot = await api.getScreenshot(connectedDevice);
      const finalLog = [...currentActivityLog];
      const finalFrames = [...recordedFramesRef.current];

      const response: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: result.success ? '**Done!**' : `**Error:** ${result.error}`,
        timestamp: new Date(),
        screenshot: finalScreenshot.data || undefined,
        activityLog: finalLog,
        recordedFrames: finalFrames.length > 0 ? finalFrames : undefined,
        videoUrl: result.videoUrl,
      };
      setChatMessages(prev => [...prev, response]);
      if (finalScreenshot.data) setScreenshot(finalScreenshot.data);
    }

    setIsThinking(false);
  }

  // Run a specific test case from the portal
  async function runSpecificTest(testCase: string) {
    if (isThinking || runningTestId) return;

    setRunningTestId(testCase);
    setCurrentActivityLog([]);

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      role: 'user',
      content: `Run test: ${testCase}`,
      timestamp: new Date(),
    };
    setChatMessages(prev => [...prev, userMessage]);
    setIsThinking(true);

    const startTime = Date.now();

    // Run the test
    const runActivityId = addActivity({
      type: 'tool',
      tool: 'stb_run_test',
      command: `api.runTest("${connectedDevice}", "HEAD", ["${testCase}"])`,
      status: 'running',
    });

    const runResult = await api.runTest(connectedDevice, 'HEAD', [testCase]);

    if (runResult.error || !runResult.data?.job_uid) {
      updateActivity(runActivityId, {
        status: 'error',
        output: [runResult.error || 'Failed to start test'],
        duration: Date.now() - startTime,
      });

      const finalLog = [...currentActivityLog];
      const response: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: `**Failed to start test:** ${runResult.error || 'Unknown error'}`,
        timestamp: new Date(),
        activityLog: finalLog,
      };
      setChatMessages(prev => [...prev, response]);
    } else {
      const jobUid = runResult.data.job_uid;
      // Track the running job for status display and cancel functionality
      setRunningJob({ jobUid, testCase });

      updateActivity(runActivityId, {
        status: 'done',
        output: [`Job started: ${jobUid}`],
        duration: Date.now() - startTime,
      });

      // Wait for completion
      const awaitStartTime = Date.now();
      const awaitActivityId = addActivity({
        type: 'tool',
        tool: 'stb_await_completion',
        command: `api.awaitJobCompletion("${jobUid}")`,
        status: 'running',
      });

      const completionResult = await api.awaitJobCompletion(jobUid);

      if (completionResult.error) {
        updateActivity(awaitActivityId, {
          status: 'error',
          output: [completionResult.error],
          duration: Date.now() - awaitStartTime,
        });
      } else {
        const result = completionResult.data?.result || 'unknown';
        const resultUrl = completionResult.data?.result_url || '';

        updateActivity(awaitActivityId, {
          status: 'done',
          output: [`Result: ${result}`, `URL: ${resultUrl}`],
          duration: Date.now() - awaitStartTime,
        });
      }

      const finalScreenshot = await api.getScreenshot(connectedDevice);
      if (finalScreenshot.data) setScreenshot(finalScreenshot.data);

      const finalLog = [...currentActivityLog];
      const jobResult = completionResult.data;
      const triageUrl = jobResult?.result_url?.replace('/api/v2/results/', '/app/#/result/') || '';

      const response: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: `**Test Completed!**\n\n**Test:** ${testCase}\n**Result:** ${jobResult?.result || 'unknown'}\n${jobResult?.failure_reason ? `**Failure:** ${jobResult.failure_reason}\n` : ''}\n**📹 Video URL:**\n${triageUrl}`,
        timestamp: new Date(),
        screenshot: finalScreenshot.data || undefined,
        activityLog: finalLog,
      };
      setChatMessages(prev => [...prev, response]);
    }

    setIsThinking(false);
    setRunningTestId(null);
    setRunningJob(null);
  }

  // Cancel running test
  async function cancelRunningTest() {
    if (!runningJob) return;

    const cancelActivityId = addActivity({
      type: 'tool',
      tool: 'stb_cancel_job',
      command: `api.cancelJob("${runningJob.jobUid}")`,
      status: 'running',
    });

    const result = await api.cancelJob(runningJob.jobUid);

    if (result.error) {
      updateActivity(cancelActivityId, {
        status: 'error',
        output: [result.error],
        duration: 0,
      });
    } else {
      updateActivity(cancelActivityId, {
        status: 'done',
        output: ['Test cancelled'],
        duration: 0,
      });
    }

    const finalLog = [...currentActivityLog];
    const response: ChatMessage = {
      id: (Date.now() + 1).toString(),
      role: 'assistant',
      content: result.error
        ? `**Failed to cancel test:** ${result.error}`
        : `**Test Cancelled**\n\nTest "${runningJob.testCase}" was cancelled.`,
      timestamp: new Date(),
      activityLog: finalLog,
    };
    setChatMessages(prev => [...prev, response]);

    setIsThinking(false);
    setRunningTestId(null);
    setRunningJob(null);
  }

  return (
    <div className="flex h-screen bg-[var(--bg-primary)] transition-colors duration-200">
      {/* Sidebar */}
      <aside className="w-14 bg-[var(--bg-primary)] border-r border-[var(--border-primary)] flex flex-col items-center py-4 transition-colors duration-200">
        <button className="mb-4 p-2 hover:bg-[var(--bg-tertiary)] rounded-lg transition-colors">
          <SidebarIcon />
        </button>

        <nav className="flex-1 flex flex-col items-center gap-1">
          <NavButton icon={<ChatIcon />} active={activeTab === 'chat'} onClick={() => setActiveTab('chat')} />
          <NavButton icon={<TestIcon />} active={activeTab === 'testcases'} onClick={() => setActiveTab('testcases')} />
          <NavButton icon={<ResultsIcon />} active={activeTab === 'results'} onClick={() => setActiveTab('results')} />
          <NavButton icon={<DeviceIcon />} active={activeTab === 'devices'} onClick={() => setActiveTab('devices')} />
          <NavButton icon={<MCPIcon />} active={activeTab === 'mcp'} onClick={() => setActiveTab('mcp')} />
        </nav>

        {/* Dark Mode Toggle */}
        <button
          onClick={() => setDarkMode(!darkMode)}
          className="mb-3 p-2 hover:bg-[var(--bg-tertiary)] rounded-lg transition-colors"
          title={darkMode ? 'Switch to Light Mode' : 'Switch to Dark Mode'}
        >
          {darkMode ? (
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="var(--text-secondary)" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <circle cx="12" cy="12" r="5" />
              <line x1="12" y1="1" x2="12" y2="3" />
              <line x1="12" y1="21" x2="12" y2="23" />
              <line x1="4.22" y1="4.22" x2="5.64" y2="5.64" />
              <line x1="18.36" y1="18.36" x2="19.78" y2="19.78" />
              <line x1="1" y1="12" x2="3" y2="12" />
              <line x1="21" y1="12" x2="23" y2="12" />
              <line x1="4.22" y1="19.78" x2="5.64" y2="18.36" />
              <line x1="18.36" y1="5.64" x2="19.78" y2="4.22" />
            </svg>
          ) : (
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="var(--text-secondary)" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z" />
            </svg>
          )}
        </button>

        <div className="w-9 h-9 rounded-full bg-[var(--text-primary)] flex items-center justify-center text-[var(--bg-primary)] text-sm font-medium">
          S
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 flex flex-col overflow-hidden">
        {activeTab === 'chat' && (
          <ChatView
            messages={chatMessages}
            input={input}
            setInput={setInput}
            isThinking={isThinking}
            onSend={handleSendMessage}
            screenshot={screenshot}
            onTakeScreenshot={takeScreenshot}
            onSendKey={sendKey}
            connectedDevice={connectedDevice}
            currentActivityLog={currentActivityLog}
            availableTests={availableTests}
            onRunTest={runSpecificTest}
            runningTestId={runningTestId}
            showTestListRequest={showTestListRequest}
            runningJob={runningJob}
            onCancelTest={cancelRunningTest}
          />
        )}

        {activeTab === 'testcases' && (
          <TestCasesView testCases={testCases} />
        )}

        {activeTab === 'results' && (
          <ResultsView results={results} />
        )}

        {activeTab === 'devices' && (
          <DevicesView
            devices={devices}
            connectedDevice={connectedDevice}
            onConnect={setConnectedDevice}
            onRefresh={loadDevices}
          />
        )}

        {activeTab === 'mcp' && (
          <MCPView
            tools={MCP_TOOLS}
            onUseInChat={(tool) => {
              // Build command with parameter placeholders
              const params = tool.parameters
                .filter(p => p.required)
                .map(p => `${p.name}="<${p.type}>"`)
                .join(' ');
              const command = params
                ? `use ${tool.name} with ${params}`
                : `use ${tool.name}`;
              setInput(command);
              setActiveTab('chat');
            }}
          />
        )}
      </main>
    </div>
  );
}

// ============ Views ============

function ChatView({
  messages, input, setInput, isThinking, onSend, screenshot, onTakeScreenshot, onSendKey, connectedDevice, currentActivityLog, availableTests, onRunTest, runningTestId, showTestListRequest, runningJob, onCancelTest
}: {
  messages: ChatMessage[];
  input: string;
  setInput: (v: string) => void;
  isThinking: boolean;
  onSend: () => void;
  screenshot: string | null;
  onTakeScreenshot: () => void;
  onSendKey: (key: string) => void;
  connectedDevice: string;
  currentActivityLog: ActivityLogEntry[];
  availableTests: string[];
  onRunTest: (testCase: string) => void;
  runningTestId: string | null;
  showTestListRequest: number;
  runningJob: { jobUid: string; testCase: string } | null;
  onCancelTest: () => void;
}) {
  const [playingRecording, setPlayingRecording] = useState<{ frames?: RecordedFrame[]; videoUrl?: string } | null>(null);
  const [showLiveStream, setShowLiveStream] = useState(false);
  const [testFilter, setTestFilter] = useState('');
  const [showTestList, setShowTestList] = useState(false);

  // Show test list modal when explicitly requested
  useEffect(() => {
    if (showTestListRequest > 0 && availableTests.length > 0) {
      setShowTestList(true);
    }
  }, [showTestListRequest, availableTests]);
  const liveStreamUrl = api.getLiveStreamUrl(connectedDevice);

  return (
    <div className="flex-1 flex overflow-hidden">
      {/* Chat Area */}
      <div className="flex-1 flex flex-col min-h-0">
        {/* Device indicator */}
        <div className="px-6 py-3 border-b border-[var(--border-primary)] flex items-center justify-between bg-[var(--bg-secondary)] flex-shrink-0">
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 bg-green-500 rounded-full"></div>
            <span className="text-sm text-[var(--text-secondary)]">Connected: {connectedDevice}</span>
          </div>
          <button onClick={onTakeScreenshot} className="text-sm text-[var(--accent)] hover:underline">
            Refresh Screenshot
          </button>
        </div>

        {/* Running Test Status Banner */}
        {runningJob && (
          <div className="px-6 py-3 bg-yellow-50 border-b border-yellow-200 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-4 h-4 border-2 border-yellow-500 border-t-transparent rounded-full animate-spin"></div>
              <div>
                <span className="text-sm font-medium text-yellow-800">Test Running: </span>
                <span className="text-sm text-yellow-700">{runningJob.testCase.split('::').pop()}</span>
                <span className="text-xs text-yellow-600 ml-2">(Job: {runningJob.jobUid})</span>
              </div>
            </div>
            <button
              onClick={onCancelTest}
              className="px-3 py-1.5 bg-red-500 hover:bg-red-600 text-white text-sm font-medium rounded-lg flex items-center gap-2 transition-colors"
            >
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <rect x="3" y="3" width="18" height="18" rx="2" />
              </svg>
              Cancel Test
            </button>
          </div>
        )}

        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-6 min-h-0">
          {messages.length === 0 ? (
            <div className="h-full flex flex-col items-center justify-center">
              <ClaudeLogo size={48} />
              <h1 className="text-3xl font-semibold text-[var(--text-primary)] mt-4">
                Ziggo Vibe Test
              </h1>
              <p className="text-[var(--text-secondary)] mb-8">Create STB tester test cases on the fly</p>
              <div className="flex gap-2 flex-wrap justify-center">
                <QuickAction label="📸 Screenshot" onClick={() => setInput('Take a screenshot')} />
                <QuickAction label="📋 List Tests" onClick={() => setInput('List all tests')} />
                <QuickAction label="🧪 Run Test" onClick={() => setInput('Run test')} />
                <QuickAction label="🎮 Press Menu" onClick={() => setInput('Press menu')} />
                <QuickAction label="📺 Open EPG" onClick={() => setInput('Press EPG')} />
                <QuickAction label="📱 List Devices" onClick={() => setInput('List devices')} />
              </div>
            </div>
          ) : (
            <div className="max-w-3xl mx-auto space-y-4">
              {messages.map(msg => (
                <div key={msg.id} className={`flex gap-3 ${msg.role === 'user' ? 'flex-row-reverse' : ''}`}>
                  <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${
                    msg.role === 'user' ? 'bg-[var(--text-primary)] text-white' : 'bg-[var(--accent)]'
                  }`}>
                    {msg.role === 'user' ? 'S' : <ClaudeLogo size={16} />}
                  </div>
                  <div className={`max-w-[85%] ${msg.role === 'user' ? 'text-right' : ''}`}>
                    {/* Activity Log for assistant messages */}
                    {msg.role === 'assistant' && msg.activityLog && msg.activityLog.length > 0 && (
                      <ActivityLog entries={msg.activityLog} />
                    )}
                    <div className={`inline-block px-4 py-3 rounded-2xl ${
                      msg.role === 'user' ? 'bg-[var(--text-primary)] text-white' : 'bg-[var(--bg-secondary)] border border-[var(--border-primary)]'
                    }`}>
                      <p className="whitespace-pre-wrap text-sm">{msg.content}</p>
                    </div>
                    {/* Play Recording button */}
                    {(msg.videoUrl || (msg.recordedFrames && msg.recordedFrames.length > 1)) && (
                      <button
                        onClick={() => setPlayingRecording({
                          frames: msg.recordedFrames,
                          videoUrl: msg.videoUrl
                        })}
                        className="mt-2 flex items-center gap-2 px-4 py-2 bg-[var(--accent)] hover:bg-[var(--accent-hover)] text-white rounded-lg text-sm font-medium transition-colors"
                      >
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                          <path d="M8 5v14l11-7z" />
                        </svg>
                        {msg.videoUrl ? 'Play Video' : `Play Recording (${msg.recordedFrames?.length} frames)`}
                      </button>
                    )}
                    {msg.screenshot && (
                      <img src={msg.screenshot} alt="Screenshot" className="mt-2 rounded-lg border border-[var(--border-primary)] max-w-full" />
                    )}
                  </div>
                </div>
              ))}
              {isThinking && (
                <div className="flex gap-3">
                  <div className="w-8 h-8 rounded-full bg-[var(--accent)] flex items-center justify-center">
                    <ClaudeLogo size={16} />
                  </div>
                  <div className="max-w-[85%]">
                    {/* Live Activity Log while thinking */}
                    {currentActivityLog.length > 0 && (
                      <ActivityLog entries={currentActivityLog} isLive />
                    )}
                    {currentActivityLog.length === 0 && (
                      <div className="flex items-center gap-1 pt-2">
                        <div className="w-2 h-2 bg-[var(--accent)] rounded-full animate-bounce" />
                        <div className="w-2 h-2 bg-[var(--accent)] rounded-full animate-bounce" style={{ animationDelay: '0.1s' }} />
                        <div className="w-2 h-2 bg-[var(--accent)] rounded-full animate-bounce" style={{ animationDelay: '0.2s' }} />
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* Show button to open test list if tests are available */}
              {availableTests.length > 0 && !isThinking && (
                <div className="mt-4 text-center">
                  <button
                    onClick={() => setShowTestList(true)}
                    className="px-6 py-2 bg-[var(--accent)] hover:bg-[var(--accent-hover)] text-white rounded-lg font-medium"
                  >
                    📋 View {availableTests.length} Test Cases
                  </button>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Input */}
        <div className="p-4 border-t border-[var(--border-primary)] flex-shrink-0 bg-[var(--bg-primary)]">
          <div className="max-w-3xl mx-auto">
            <div className="bg-[var(--bg-secondary)] rounded-2xl border border-[var(--border-primary)] overflow-hidden">
              <textarea
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    onSend();
                  }
                }}
                placeholder="Type a command... (e.g., 'take a screenshot', 'press OK')"
                rows={1}
                className="w-full px-4 py-3 text-sm resize-none focus:outline-none"
              />
              <div className="flex justify-end px-3 py-2 border-t border-[var(--border-secondary)]">
                <button
                  onClick={onSend}
                  disabled={!input.trim()}
                  className={`w-8 h-8 rounded-full flex items-center justify-center ${
                    input.trim() ? 'bg-[var(--accent)] text-white' : 'bg-[var(--bg-tertiary)] text-[var(--text-tertiary)]'
                  }`}
                >
                  <ArrowUpIcon />
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Screenshot Panel */}
      {screenshot && (
        <div className="w-[400px] border-l border-[var(--border-primary)] bg-[var(--bg-secondary)] p-4 flex flex-col overflow-y-auto flex-shrink-0">
          <div className="flex items-center justify-between mb-3">
            <h3 className="font-medium">Live Screen</h3>
            <button
              onClick={() => setShowLiveStream(true)}
              className="flex items-center gap-1 px-2 py-1 text-xs bg-[var(--accent)] hover:bg-[var(--accent-hover)] text-white rounded-lg"
            >
              <svg width="12" height="12" viewBox="0 0 24 24" fill="currentColor">
                <path d="M8 5v14l11-7z" />
              </svg>
              Videos
            </button>
          </div>
          <img src={screenshot} alt="Device screen" className="rounded-lg border border-[var(--border-primary)] mb-4" />

          <h4 className="text-sm font-medium mb-2 text-[var(--text-secondary)]">Remote Control</h4>
          <div className="grid grid-cols-3 gap-2">
            <div></div>
            <RemoteButton label="▲" onClick={() => onSendKey('KEY_UP')} />
            <div></div>
            <RemoteButton label="◀" onClick={() => onSendKey('KEY_LEFT')} />
            <RemoteButton label="OK" onClick={() => onSendKey('KEY_OK')} />
            <RemoteButton label="▶" onClick={() => onSendKey('KEY_RIGHT')} />
            <div></div>
            <RemoteButton label="▼" onClick={() => onSendKey('KEY_DOWN')} />
            <div></div>
          </div>
          <div className="flex gap-2 mt-3">
            <RemoteButton label="Back" onClick={() => onSendKey('KEY_BACK')} className="flex-1" />
            <RemoteButton label="Home" onClick={() => onSendKey('KEY_HOME')} className="flex-1" />
            <RemoteButton label="Menu" onClick={() => onSendKey('KEY_MENU')} className="flex-1" />
          </div>
        </div>
      )}

      {/* Video Player Modal */}
      {playingRecording && (
        <VideoPlayer
          frames={playingRecording.frames}
          videoUrl={playingRecording.videoUrl}
          onClose={() => setPlayingRecording(null)}
        />
      )}

      {/* Live Stream Modal */}
      {showLiveStream && (
        <LiveStreamPlayer
          streamUrl={liveStreamUrl}
          deviceId={connectedDevice}
          onClose={() => setShowLiveStream(false)}
        />
      )}

      {/* Test List Modal */}
      {showTestList && availableTests.length > 0 && (
        <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-50" onClick={() => setShowTestList(false)}>
          <div className="bg-[var(--bg-secondary)] rounded-2xl max-w-3xl w-full mx-4 max-h-[80vh] overflow-hidden shadow-2xl" onClick={e => e.stopPropagation()}>
            {/* Header */}
            <div className="flex items-center justify-between px-4 py-3 border-b border-[var(--border-primary)]">
              <div className="flex items-center gap-3">
                <span className="text-lg font-medium">📋 Available Test Cases</span>
                <span className="text-sm text-[var(--text-secondary)]">{availableTests.length} tests</span>
              </div>
              <button onClick={() => setShowTestList(false)} className="p-1 hover:bg-[var(--bg-primary)] rounded-lg">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="var(--text-secondary)" strokeWidth="2">
                  <path d="M18 6L6 18M6 6l12 12" strokeLinecap="round" />
                </svg>
              </button>
            </div>

            {/* Filter */}
            <div className="px-4 py-3 border-b border-[var(--border-primary)] bg-[var(--bg-primary)]">
              <input
                type="text"
                placeholder="🔍 Filter tests by name..."
                value={testFilter}
                onChange={(e) => setTestFilter(e.target.value)}
                className="w-full px-4 py-2 text-sm border border-[var(--border-primary)] rounded-lg focus:outline-none focus:border-[var(--accent)] bg-[var(--bg-secondary)]"
              />
            </div>

            {/* Test List */}
            <div className="overflow-y-auto max-h-[50vh] p-4 space-y-2">
              {availableTests
                .filter(tc => tc.toLowerCase().includes(testFilter.toLowerCase()))
                .map((tc, index) => {
                  const testName = tc.split('::').pop() || tc;
                  const testFile = tc.split('::')[0] || '';
                  const isRunning = runningTestId === tc;

                  return (
                    <div
                      key={index}
                      className="flex items-center justify-between p-3 bg-[var(--bg-primary)] rounded-lg hover:bg-[var(--bg-tertiary)] transition-colors"
                    >
                      <div className="flex-1 min-w-0 mr-3">
                        <div className="font-medium text-sm">{testName}</div>
                        <div className="text-xs text-[var(--text-tertiary)] truncate">{testFile}</div>
                      </div>
                      <button
                        onClick={() => {
                          setShowTestList(false);
                          onRunTest(tc);
                        }}
                        disabled={isThinking || !!runningTestId}
                        className={`px-4 py-1.5 rounded-lg text-sm font-medium transition-colors flex items-center gap-2 ${
                          isRunning
                            ? 'bg-yellow-500 text-white'
                            : isThinking || runningTestId
                            ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                            : 'bg-[var(--accent)] hover:bg-[var(--accent-hover)] text-white'
                        }`}
                      >
                        {isRunning ? (
                          <>
                            <div className="w-3 h-3 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                            Running...
                          </>
                        ) : (
                          <>
                            <svg width="12" height="12" viewBox="0 0 24 24" fill="currentColor">
                              <path d="M8 5v14l11-7z" />
                            </svg>
                            Run
                          </>
                        )}
                      </button>
                    </div>
                  );
                })}
            </div>

            {/* Footer */}
            <div className="px-4 py-3 border-t border-[var(--border-primary)] bg-[var(--bg-primary)] text-center">
              <p className="text-xs text-[var(--text-tertiary)]">
                Click "Run" to execute a test on device {connectedDevice}
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

function TestCasesView({ testCases }: { testCases: TestCase[] }) {
  return (
    <div className="flex-1 p-8 overflow-y-auto">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-normal text-[var(--text-primary)] mb-6">Test Cases</h1>
        <div className="space-y-3">
          {testCases.map(tc => (
            <div key={tc.id} className="bg-[var(--bg-secondary)] border border-[var(--border-primary)] rounded-xl p-5 flex items-center justify-between">
              <div>
                <div className="flex items-center gap-3 mb-1">
                  <h3 className="font-medium">{tc.name}</h3>
                  <StatusBadge status={tc.status} />
                </div>
                <p className="text-sm text-[var(--text-secondary)]">{tc.description}</p>
              </div>
              <button className="px-4 py-2 bg-[var(--accent)] text-white rounded-lg text-sm font-medium hover:bg-[var(--accent-hover)]">
                Run
              </button>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

function ResultsView({ results }: { results: TestResult[] }) {
  return (
    <div className="flex-1 p-8 overflow-y-auto">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-normal text-[var(--text-primary)] mb-6">Test Results</h1>
        {results.length === 0 ? (
          <div className="text-center py-16 text-[var(--text-secondary)]">
            <p>No test results yet. Run a test to see results here.</p>
          </div>
        ) : (
          <div className="space-y-3">
            {results.map(r => (
              <div key={r.id} className="bg-[var(--bg-secondary)] border border-[var(--border-primary)] rounded-xl p-5">
                <div className="flex items-center gap-3">
                  <ResultBadge status={r.status} />
                  <div>
                    <h3 className="font-medium">{r.testCaseName}</h3>
                    <p className="text-sm text-[var(--text-secondary)]">{r.completedAt.toLocaleString()}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

function DevicesView({
  devices, connectedDevice, onConnect, onRefresh
}: {
  devices: api.STBDevice[];
  connectedDevice: string;
  onConnect: (id: string) => void;
  onRefresh: () => void;
}) {
  return (
    <div className="flex-1 p-8 overflow-y-auto">
      <div className="max-w-4xl mx-auto">
        <div className="flex items-center justify-between mb-6">
          <h1 className="text-3xl font-normal text-[var(--text-primary)]">Devices</h1>
          <button
            onClick={onRefresh}
            className="px-4 py-2 bg-[var(--text-primary)] text-white rounded-lg text-sm font-medium hover:bg-[var(--bg-tertiary)]"
          >
            Refresh
          </button>
        </div>

        {devices.length === 0 ? (
          <div className="text-center py-16 text-[var(--text-secondary)]">
            <p>Loading devices...</p>
          </div>
        ) : (
          <div className="space-y-3">
            {devices.map(device => (
              <div
                key={device.node_id}
                className={`bg-[var(--bg-secondary)] border rounded-xl p-5 cursor-pointer transition-all ${
                  device.node_id === connectedDevice
                    ? 'border-[var(--accent)] shadow-md'
                    : 'border-[var(--border-primary)] hover:border-[var(--text-tertiary)]'
                }`}
                onClick={() => onConnect(device.node_id)}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className={`w-3 h-3 rounded-full ${
                      device.state === 'idle' ? 'bg-green-500' : 'bg-yellow-500'
                    }`} />
                    <div>
                      <h3 className="font-medium">{device.node_id}</h3>
                      <p className="text-sm text-[var(--text-secondary)]">State: {device.state}</p>
                    </div>
                  </div>
                  {device.node_id === connectedDevice && (
                    <span className="text-sm text-[var(--accent)] font-medium">Connected</span>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

function MCPView({
  tools, onUseInChat
}: {
  tools: MCPTool[];
  onUseInChat: (tool: MCPTool) => void;
}) {
  const categories = [
    { key: 'device' as const, label: 'Device Management', icon: '📱' },
    { key: 'control' as const, label: 'Remote Control', icon: '🎮' },
    { key: 'verify' as const, label: 'Verification', icon: '✅' },
    { key: 'navigate' as const, label: 'Navigation', icon: '🧭' },
  ];

  return (
    <div className="flex-1 p-8 overflow-y-auto">
      <div className="max-w-4xl mx-auto">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-3xl font-normal text-[var(--text-primary)]">MCP Tools</h1>
            <p className="text-sm text-[var(--text-secondary)] mt-1">Model Context Protocol tools for STB Tester</p>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 bg-green-500 rounded-full"></div>
            <span className="text-sm text-[var(--text-secondary)]">Server Connected</span>
          </div>
        </div>

        {categories.map(category => {
          const categoryTools = tools.filter(t => t.category === category.key);
          if (categoryTools.length === 0) return null;

          return (
            <div key={category.key} className="mb-8">
              <h2 className="text-lg font-medium text-[var(--text-primary)] mb-3 flex items-center gap-2">
                <span>{category.icon}</span>
                {category.label}
              </h2>
              <div className="grid gap-3">
                {categoryTools.map(tool => (
                  <div
                    key={tool.name}
                    className="bg-[var(--bg-secondary)] border border-[var(--border-primary)] rounded-xl p-4 hover:border-[var(--accent)] transition-colors"
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <h3 className="font-mono text-sm font-medium text-[var(--accent)]">{tool.name}</h3>
                        <p className="text-sm text-[var(--text-secondary)] mt-1">{tool.description}</p>
                        {tool.parameters.length > 0 && (
                          <div className="mt-2 flex flex-wrap gap-1">
                            {tool.parameters.map(param => (
                              <span
                                key={param.name}
                                className={`text-xs px-2 py-0.5 rounded-full ${
                                  param.required
                                    ? 'bg-[var(--accent)]/10 text-[var(--accent)]'
                                    : 'bg-gray-100 text-gray-600'
                                }`}
                                title={param.description}
                              >
                                {param.name}: {param.type}
                                {param.required && ' *'}
                              </span>
                            ))}
                          </div>
                        )}
                      </div>
                      <button
                        onClick={() => onUseInChat(tool)}
                        className="ml-4 px-3 py-1.5 bg-[var(--bg-primary)] hover:bg-[var(--bg-tertiary)] rounded-lg text-sm font-medium transition-colors"
                      >
                        Use in Chat
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

// ============ Activity Log Component (Claude Code Style) ============

function ActivityLog({ entries, isLive = false }: { entries: ActivityLogEntry[]; isLive?: boolean }) {
  const [expandedEntries, setExpandedEntries] = useState<Set<string>>(new Set());

  const toggleExpand = (id: string) => {
    setExpandedEntries(prev => {
      const next = new Set(prev);
      if (next.has(id)) {
        next.delete(id);
      } else {
        next.add(id);
      }
      return next;
    });
  };

  const formatDuration = (ms?: number) => {
    if (!ms) return '';
    if (ms < 1000) return `${ms}ms`;
    return `${(ms / 1000).toFixed(1)}s`;
  };

  return (
    <div className="mb-3 font-mono text-xs">
      {entries.map((entry, index) => {
        const isExpanded = expandedEntries.has(entry.id);
        const isLastEntry = index === entries.length - 1;
        const showSpinner = isLive && isLastEntry && entry.status === 'running';

        return (
          <div key={entry.id} className="mb-1">
            {/* Tool header line */}
            <div className="flex items-start gap-2">
              {/* Status indicator */}
              <span className="flex-shrink-0 mt-0.5">
                {entry.status === 'running' ? (
                  <span className="inline-block w-2 h-2 bg-yellow-500 rounded-full animate-pulse" />
                ) : entry.status === 'error' ? (
                  <span className="inline-block w-2 h-2 bg-red-500 rounded-full" />
                ) : (
                  <span className="inline-block w-2 h-2 bg-green-500 rounded-full" />
                )}
              </span>

              {/* Tool info */}
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 flex-wrap">
                  <span className="text-[var(--accent)] font-semibold">{entry.tool}</span>
                  <span className="text-[var(--text-tertiary)] truncate">({entry.command})</span>
                  {entry.duration && (
                    <span className="text-[var(--text-secondary)]">{formatDuration(entry.duration)}</span>
                  )}
                </div>

                {/* Output lines */}
                {entry.output && entry.output.length > 0 && (
                  <div className="mt-0.5 text-[var(--text-tertiary)]">
                    {entry.output.length <= 2 || isExpanded ? (
                      // Show all lines
                      entry.output.map((line, i) => (
                        <div key={i} className="pl-2 border-l-2 border-[var(--border-primary)]">
                          {line.length > 80 ? `${line.substring(0, 80)}...` : line}
                        </div>
                      ))
                    ) : (
                      // Show collapsed view
                      <>
                        <div className="pl-2 border-l-2 border-[var(--border-primary)]">
                          {entry.output[0].length > 80 ? `${entry.output[0].substring(0, 80)}...` : entry.output[0]}
                        </div>
                        <button
                          onClick={() => toggleExpand(entry.id)}
                          className="pl-2 text-[var(--text-secondary)] hover:text-[var(--accent)] cursor-pointer"
                        >
                          ... +{entry.output.length - 1} lines (click to expand)
                        </button>
                      </>
                    )}
                    {entry.output.length > 2 && isExpanded && (
                      <button
                        onClick={() => toggleExpand(entry.id)}
                        className="pl-2 text-[var(--text-secondary)] hover:text-[var(--accent)] cursor-pointer"
                      >
                        (click to collapse)
                      </button>
                    )}
                  </div>
                )}

                {/* Spinner for running state */}
                {showSpinner && (
                  <div className="flex items-center gap-1 mt-1 text-[var(--text-tertiary)]">
                    <span className="inline-block w-1 h-1 bg-[var(--text-tertiary)] rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                    <span className="inline-block w-1 h-1 bg-[var(--text-tertiary)] rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                    <span className="inline-block w-1 h-1 bg-[var(--text-tertiary)] rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                  </div>
                )}
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}

// ============ Video Player Component ============

function VideoPlayer({
  frames,
  videoUrl,
  onClose
}: {
  frames?: RecordedFrame[];
  videoUrl?: string;
  onClose: () => void;
}) {
  const videoRef = useRef<HTMLVideoElement>(null);
  const [currentFrame, setCurrentFrame] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);
  const [playbackSpeed, setPlaybackSpeed] = useState(1);
  const [videoError, setVideoError] = useState<string | null>(null);

  // For frame slideshow mode
  useEffect(() => {
    if (videoUrl || !frames) return;

    if (!isPlaying || currentFrame >= frames.length - 1) {
      if (currentFrame >= frames.length - 1) {
        setIsPlaying(false);
      }
      return;
    }

    const interval = setInterval(() => {
      setCurrentFrame(prev => {
        if (prev >= frames.length - 1) {
          setIsPlaying(false);
          return prev;
        }
        return prev + 1;
      });
    }, 1000 / playbackSpeed);

    return () => clearInterval(interval);
  }, [isPlaying, currentFrame, frames, playbackSpeed, videoUrl]);

  // Sync video playback speed
  useEffect(() => {
    if (videoRef.current) {
      videoRef.current.playbackRate = playbackSpeed;
    }
  }, [playbackSpeed]);

  const handlePlayPause = () => {
    if (videoUrl && videoRef.current) {
      if (isPlaying) {
        videoRef.current.pause();
      } else {
        videoRef.current.play();
      }
      setIsPlaying(!isPlaying);
    } else if (frames) {
      if (currentFrame >= frames.length - 1) {
        setCurrentFrame(0);
      }
      setIsPlaying(!isPlaying);
    }
  };

  const handleSeek = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (frames) {
      setCurrentFrame(parseInt(e.target.value));
      setIsPlaying(false);
    }
  };

  const handleVideoError = () => {
    setVideoError('Failed to load video. The video may not be available yet.');
  };

  const frame = frames?.[currentFrame];
  const isVideoMode = !!videoUrl;

  return (
    <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-50" onClick={onClose}>
      <div className="bg-[var(--bg-secondary)] rounded-2xl max-w-4xl w-full mx-4 overflow-hidden shadow-2xl" onClick={e => e.stopPropagation()}>
        {/* Header */}
        <div className="flex items-center justify-between px-4 py-3 border-b border-[var(--border-primary)]">
          <div className="flex items-center gap-3">
            <span className="text-lg font-medium">Test Recording</span>
            {isVideoMode ? (
              <span className="text-sm text-[var(--text-secondary)] flex items-center gap-1">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <rect x="2" y="4" width="20" height="16" rx="2" />
                  <path d="M10 9l5 3-5 3V9z" fill="currentColor" />
                </svg>
                Video
              </span>
            ) : (
              <span className="text-sm text-[var(--text-secondary)]">{frames?.length || 0} frames</span>
            )}
          </div>
          <button onClick={onClose} className="p-1 hover:bg-[var(--bg-primary)] rounded-lg">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="var(--text-secondary)" strokeWidth="2">
              <path d="M18 6L6 18M6 6l12 12" strokeLinecap="round" />
            </svg>
          </button>
        </div>

        {/* Video/Frame Display */}
        <div className="relative bg-black min-h-[300px] flex items-center justify-center">
          {isVideoMode ? (
            videoError ? (
              <div className="text-white text-center p-8">
                <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="mx-auto mb-4 opacity-50">
                  <circle cx="12" cy="12" r="10" />
                  <path d="M12 8v4M12 16h.01" />
                </svg>
                <p>{videoError}</p>
                {frames && frames.length > 0 && (
                  <button
                    onClick={() => setVideoError(null)}
                    className="mt-4 px-4 py-2 bg-[var(--accent)] rounded-lg text-sm"
                  >
                    View Screenshots Instead
                  </button>
                )}
              </div>
            ) : (
              <video
                ref={videoRef}
                src={videoUrl}
                className="w-full h-auto max-h-[60vh] object-contain"
                controls
                autoPlay
                onPlay={() => setIsPlaying(true)}
                onPause={() => setIsPlaying(false)}
                onError={handleVideoError}
              >
                Your browser does not support video playback.
              </video>
            )
          ) : frame ? (
            <>
              <img
                src={frame.screenshot}
                alt={`Frame ${currentFrame + 1}`}
                className="w-full h-auto max-h-[60vh] object-contain transition-opacity duration-200"
              />
              {/* Frame Label */}
              {frame.label && (
                <div className="absolute top-4 left-4 bg-black/70 text-white px-3 py-1 rounded-lg text-sm font-medium">
                  {frame.label}
                </div>
              )}
              {/* Frame Counter */}
              <div className="absolute top-4 right-4 bg-black/70 text-white px-3 py-1 rounded-lg text-sm font-mono">
                {currentFrame + 1} / {frames?.length || 0}
              </div>
            </>
          ) : (
            <div className="text-white text-center p-8">No recording available</div>
          )}
        </div>

        {/* Controls - only show for frame mode or when video has error */}
        {!isVideoMode && frames && frames.length > 0 && (
          <div className="p-4 bg-[var(--bg-primary)]">
            {/* Timeline */}
            <div className="mb-4">
              <input
                type="range"
                min="0"
                max={frames.length - 1}
                value={currentFrame}
                onChange={handleSeek}
                className="w-full h-2 bg-[var(--border-primary)] rounded-lg appearance-none cursor-pointer accent-[var(--accent)]"
              />
              <div className="flex justify-between text-xs text-[var(--text-secondary)] mt-1">
                {frames.slice(0, 20).map((f, i) => (
                  <button
                    key={i}
                    onClick={() => setCurrentFrame(i)}
                    className={`w-2 h-2 rounded-full transition-colors ${
                      i === currentFrame ? 'bg-[var(--accent)]' : 'bg-[var(--border-primary)] hover:bg-[var(--border-primary)]'
                    }`}
                    title={f.label || `Frame ${i + 1}`}
                  />
                ))}
                {frames.length > 20 && <span className="text-[var(--text-tertiary)]">...</span>}
              </div>
            </div>

            {/* Playback Controls */}
            <div className="flex items-center justify-center gap-4">
              {/* Previous */}
              <button
                onClick={() => setCurrentFrame(prev => Math.max(0, prev - 1))}
                disabled={currentFrame === 0}
                className="p-2 hover:bg-[var(--bg-tertiary)] rounded-lg disabled:opacity-30"
              >
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="var(--text-secondary)" strokeWidth="2">
                  <path d="M19 20L9 12l10-8v16zM5 19V5" strokeLinecap="round" strokeLinejoin="round" />
                </svg>
              </button>

              {/* Play/Pause */}
              <button
                onClick={handlePlayPause}
                className="w-12 h-12 flex items-center justify-center bg-[var(--accent)] hover:bg-[var(--accent-hover)] rounded-full text-white"
              >
                {isPlaying ? (
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
                    <rect x="6" y="4" width="4" height="16" rx="1" />
                    <rect x="14" y="4" width="4" height="16" rx="1" />
                  </svg>
                ) : (
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M8 5v14l11-7z" />
                  </svg>
                )}
              </button>

              {/* Next */}
              <button
                onClick={() => setCurrentFrame(prev => Math.min(frames.length - 1, prev + 1))}
                disabled={currentFrame === frames.length - 1}
                className="p-2 hover:bg-[var(--bg-tertiary)] rounded-lg disabled:opacity-30"
              >
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="var(--text-secondary)" strokeWidth="2">
                  <path d="M5 4l10 8-10 8V4zM19 5v14" strokeLinecap="round" strokeLinejoin="round" />
                </svg>
              </button>

              {/* Speed */}
              <div className="ml-4 flex items-center gap-2">
                <span className="text-xs text-[var(--text-secondary)]">Speed:</span>
                {[0.5, 1, 2].map(speed => (
                  <button
                    key={speed}
                    onClick={() => setPlaybackSpeed(speed)}
                    className={`px-2 py-1 text-xs rounded ${
                      playbackSpeed === speed
                        ? 'bg-[var(--accent)] text-white'
                        : 'bg-[var(--bg-secondary)] hover:bg-[var(--bg-tertiary)]'
                    }`}
                  >
                    {speed}x
                  </button>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Speed control for video mode */}
        {isVideoMode && !videoError && (
          <div className="p-4 bg-[var(--bg-primary)] flex items-center justify-center gap-2">
            <span className="text-xs text-[var(--text-secondary)]">Playback Speed:</span>
            {[0.5, 1, 1.5, 2].map(speed => (
              <button
                key={speed}
                onClick={() => setPlaybackSpeed(speed)}
                className={`px-2 py-1 text-xs rounded ${
                  playbackSpeed === speed
                    ? 'bg-[var(--accent)] text-white'
                    : 'bg-[var(--bg-secondary)] hover:bg-[var(--bg-tertiary)]'
                }`}
              >
                {speed}x
              </button>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

// ============ Test Results Video Player Component ============

interface TestResultWithVideo {
  result_id: string;
  test_case: string;
  result: string;
  start_time: string;
  triage_url: string;
  video_url: string | null;
  has_video: boolean;
}

function LiveStreamPlayer({
  deviceId,
  onClose
}: {
  streamUrl?: string;
  deviceId: string;
  onClose: () => void;
}) {
  const [loading, setLoading] = useState(true);
  const [testResults, setTestResults] = useState<TestResultWithVideo[]>([]);
  const [selectedResult, setSelectedResult] = useState<TestResultWithVideo | null>(null);
  const [videoError, setVideoError] = useState(false);

  // Fetch test results with video info
  useEffect(() => {
    const fetchResults = async () => {
      setLoading(true);

      // Get test history
      const historyResult = await api.getTestHistory(20, { node_id: deviceId });

      if (historyResult.data && historyResult.data.length > 0) {
        // For each result, we'll check if it has video artifacts
        const resultsWithVideo: TestResultWithVideo[] = [];

        for (const r of historyResult.data.slice(0, 10)) {
          // Get detailed result to check for video artifact
          const detailResult = await fetch(`/api/v2/results${(r as { result_id?: string }).result_id || ''}`, {
            headers: { 'Authorization': `token cBqdzRDwYbX1LI6cmskfsycAXNAIZPSs` }
          });

          if (detailResult.ok) {
            const detail = await detailResult.json();
            // Build video URL from artifacts
            const hasVideo = !!detail.artifacts?.['video.mp4'];
            let videoUrl: string | null = null;
            if (hasVideo && detail.result_id) {
              // Video URL format: /api/v2/results/{result_id}/artifacts/video.mp4
              videoUrl = `/api/v2/results/${detail.result_id}/artifacts/video.mp4`;
            }
            resultsWithVideo.push({
              result_id: detail.result_id,
              test_case: detail.test_case,
              result: detail.result,
              start_time: detail.start_time,
              triage_url: detail.triage_url,
              video_url: videoUrl,
              has_video: hasVideo
            });
          }
        }

        setTestResults(resultsWithVideo);

        // Auto-select first result with video
        const firstWithVideo = resultsWithVideo.find(r => r.has_video);
        if (firstWithVideo) {
          setSelectedResult(firstWithVideo);
        } else if (resultsWithVideo.length > 0) {
          setSelectedResult(resultsWithVideo[0]);
        }
      }

      setLoading(false);
    };

    fetchResults();
  }, [deviceId]);

  // Reset video error when selecting new result
  useEffect(() => {
    setVideoError(false);
  }, [selectedResult]);

  return (
    <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-50" onClick={onClose}>
      <div className="bg-[var(--bg-secondary)] rounded-2xl max-w-6xl w-full mx-4 overflow-hidden shadow-2xl" onClick={e => e.stopPropagation()}>
        {/* Header */}
        <div className="flex items-center justify-between px-4 py-3 border-b border-[var(--border-primary)]">
          <div className="flex items-center gap-3">
            <span className="text-lg font-medium">Test Results & Videos</span>
            <span className="text-sm text-[var(--text-secondary)]">{deviceId}</span>
          </div>
          <button onClick={onClose} className="p-1 hover:bg-[var(--bg-primary)] rounded-lg">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="var(--text-secondary)" strokeWidth="2">
              <path d="M18 6L6 18M6 6l12 12" strokeLinecap="round" />
            </svg>
          </button>
        </div>

        <div className="flex" style={{ height: '70vh' }}>
          {/* Main Content - Video Player */}
          <div className="flex-1 bg-[var(--text-primary)] flex items-center justify-center">
            {loading ? (
              <div className="text-white text-center">
                <div className="w-12 h-12 border-4 border-white/30 border-t-white rounded-full animate-spin mx-auto mb-4"></div>
                <p>Loading test results...</p>
              </div>
            ) : selectedResult ? (
              selectedResult.video_url && !videoError ? (
                <video
                  key={selectedResult.result_id}
                  src={selectedResult.video_url}
                  controls
                  autoPlay
                  className="max-w-full max-h-full"
                  onError={() => setVideoError(true)}
                >
                  Your browser does not support video playback.
                </video>
              ) : (
                <div className="text-white text-center p-8">
                  <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" className="mx-auto mb-4 opacity-50">
                    <rect x="2" y="4" width="20" height="16" rx="2" />
                    <path d="M10 9l5 3-5 3V9z" fill="currentColor" />
                  </svg>
                  <p className="mb-4 text-lg">{selectedResult.has_video ? 'Video cannot be played directly' : 'No video available'}</p>
                  <p className="text-sm text-gray-400 mb-6">
                    {selectedResult.has_video
                      ? 'The video requires authentication. Open in the STB Tester portal to view.'
                      : 'This test result does not have a video recording.'}
                  </p>
                  <a
                    href={selectedResult.triage_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center gap-2 px-6 py-3 bg-[var(--accent)] hover:bg-[var(--accent-hover)] text-white rounded-lg font-medium transition-colors"
                  >
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <path d="M18 13v6a2 2 0 01-2 2H5a2 2 0 01-2-2V8a2 2 0 012-2h6M15 3h6v6M10 14L21 3" strokeLinecap="round" strokeLinejoin="round" />
                    </svg>
                    Open in STB Tester Portal
                  </a>
                </div>
              )
            ) : (
              <div className="text-white text-center p-8">
                <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="mx-auto mb-4 opacity-50">
                  <rect x="2" y="4" width="20" height="16" rx="2" />
                  <path d="M10 9l5 3-5 3V9z" fill="currentColor" />
                </svg>
                <p>No test results found for this device.</p>
              </div>
            )}
          </div>

          {/* Results List Sidebar */}
          <div className="w-72 border-l border-[var(--border-primary)] bg-[var(--bg-primary)] overflow-y-auto">
            <div className="p-3 border-b border-[var(--border-primary)]">
              <h3 className="text-sm font-medium">Test Results</h3>
              <p className="text-xs text-[var(--text-tertiary)] mt-1">Click to view result page with video</p>
            </div>
            <div className="p-2 space-y-2">
              {testResults.map((result, index) => (
                <button
                  key={result.result_id || index}
                  onClick={() => setSelectedResult(result)}
                  className={`w-full text-left p-3 rounded-lg text-xs transition-colors ${
                    selectedResult?.result_id === result.result_id
                      ? 'bg-[var(--accent)] text-white'
                      : 'bg-[var(--bg-secondary)] hover:bg-[var(--bg-tertiary)]'
                  }`}
                >
                  <div className="font-medium truncate">{result.test_case.split('::').pop()}</div>
                  <div className="text-[10px] opacity-70 truncate mt-0.5">{result.test_case.split('::')[0]}</div>
                  <div className="flex items-center justify-between mt-2">
                    <span className={`px-1.5 py-0.5 rounded text-[10px] ${
                      selectedResult?.result_id === result.result_id
                        ? 'bg-[var(--bg-secondary)]/20 text-white'
                        : result.result === 'pass' ? 'bg-green-100 text-green-700' :
                          result.result === 'fail' ? 'bg-red-100 text-red-700' :
                          'bg-yellow-100 text-yellow-700'
                    }`}>
                      {result.result}
                    </span>
                    {result.has_video && (
                      <span className={`text-[10px] ${selectedResult?.result_id === result.result_id ? 'text-white' : 'text-[var(--accent)]'}`}>
                        🎬 Has video
                      </span>
                    )}
                  </div>
                  <div className="text-[10px] opacity-70 mt-1">
                    {new Date(result.start_time).toLocaleString()}
                  </div>
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="p-3 bg-[var(--bg-primary)] border-t border-[var(--border-primary)] flex items-center justify-between">
          <p className="text-xs text-[var(--text-tertiary)]">
            Videos are embedded from the STB Tester portal. Click a test result to view its video.
          </p>
          {selectedResult && (
            <a
              href={selectedResult.triage_url}
              target="_blank"
              rel="noopener noreferrer"
              className="text-xs text-[var(--accent)] hover:underline"
            >
              Open in new tab →
            </a>
          )}
        </div>
      </div>
    </div>
  );
}

// ============ Components ============

function NavButton({ icon, active, onClick }: { icon: React.ReactNode; active?: boolean; onClick: () => void }) {
  return (
    <button
      onClick={onClick}
      className={`w-10 h-10 rounded-lg flex items-center justify-center transition-colors ${
        active ? 'bg-[var(--bg-tertiary)]' : 'hover:bg-[var(--bg-tertiary)]'
      }`}
    >
      {icon}
    </button>
  );
}

function QuickAction({ label, onClick }: { label: string; onClick: () => void }) {
  return (
    <button
      onClick={onClick}
      className="px-4 py-2 bg-[var(--bg-secondary)] border border-[var(--border-primary)] rounded-full text-sm text-[var(--text-secondary)] hover:bg-[var(--bg-primary)]"
    >
      {label}
    </button>
  );
}

function RemoteButton({ label, onClick, className = '' }: { label: string; onClick: () => void; className?: string }) {
  return (
    <button
      onClick={onClick}
      className={`py-2 bg-[var(--bg-primary)] hover:bg-[var(--bg-tertiary)] rounded-lg text-sm font-medium transition-colors ${className}`}
    >
      {label}
    </button>
  );
}

function StatusBadge({ status }: { status: string }) {
  const colors: Record<string, string> = {
    draft: 'bg-gray-100 text-gray-600',
    ready: 'bg-blue-100 text-blue-700',
    running: 'bg-yellow-100 text-yellow-700',
    passed: 'bg-green-100 text-green-700',
    failed: 'bg-red-100 text-red-700',
  };
  return (
    <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${colors[status] || colors.draft}`}>
      {status}
    </span>
  );
}

function ResultBadge({ status }: { status: string }) {
  const config: Record<string, string> = {
    passed: 'bg-green-100 text-green-700',
    failed: 'bg-red-100 text-red-700',
    error: 'bg-yellow-100 text-yellow-700',
  };
  return (
    <span className={`w-8 h-8 rounded-full flex items-center justify-center text-sm ${config[status]}`}>
      {status === 'passed' ? '✓' : '✕'}
    </span>
  );
}

// ============ Icons ============

function ClaudeLogo({ size = 24 }: { size?: number }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none">
      <path d="M12 2L14.5 9.5L22 12L14.5 14.5L12 22L9.5 14.5L2 12L9.5 9.5L12 2Z" fill="var(--accent)" />
    </svg>
  );
}

function SidebarIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="var(--text-secondary)" strokeWidth="2">
      <rect x="3" y="3" width="18" height="18" rx="2" />
      <path d="M9 3v18" />
    </svg>
  );
}

function ChatIcon() {
  return (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="var(--text-secondary)" strokeWidth="2">
      <path d="M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2z" />
    </svg>
  );
}

function TestIcon() {
  return (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="var(--text-secondary)" strokeWidth="2">
      <rect x="3" y="3" width="18" height="18" rx="2" />
      <path d="M9 9h6M9 13h6M9 17h4" strokeLinecap="round" />
    </svg>
  );
}

function ResultsIcon() {
  return (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="var(--text-secondary)" strokeWidth="2">
      <path d="M3 3v18h18" strokeLinecap="round" />
      <path d="M7 16l4-4 4 4 5-5" strokeLinecap="round" />
    </svg>
  );
}

function DeviceIcon() {
  return (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="var(--text-secondary)" strokeWidth="2">
      <rect x="2" y="3" width="20" height="14" rx="2" />
      <line x1="8" y1="21" x2="16" y2="21" />
      <line x1="12" y1="17" x2="12" y2="21" />
    </svg>
  );
}

function MCPIcon() {
  return (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="var(--text-secondary)" strokeWidth="2">
      <circle cx="12" cy="12" r="3" />
      <path d="M12 2v4M12 18v4M2 12h4M18 12h4" strokeLinecap="round" />
      <path d="M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M4.93 19.07l2.83-2.83M16.24 7.76l2.83-2.83" strokeLinecap="round" />
    </svg>
  );
}

function ArrowUpIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
      <path d="M12 19V5M5 12l7-7 7 7" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}

export default App;
