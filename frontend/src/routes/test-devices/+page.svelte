<script lang="ts">
	let microphones = $state<MediaDeviceInfo[]>([]);
	let pointerDevices = $state<string[]>([]);
	let keyboards = $state<string[]>([]);
	let error = $state<string>('');
	let loading = $state(true);
	let activeMic = $state<string | null>(null);
	let audioContext = $state<AudioContext | null>(null);
	let analyser = $state<AnalyserNode | null>(null);
	let currentStream = $state<MediaStream | null>(null);
	let audioLevels = $state<{[deviceId: string]: number}>({});

	async function detectDevices() {
		try {
			// Request microphone permission first
			await navigator.mediaDevices.getUserMedia({ audio: true });
			
			// Get all media devices
			const devices = await navigator.mediaDevices.enumerateDevices();
			microphones = devices.filter(device => device.kind === 'audioinput');

			// Stop the media stream we requested for permission
			const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
			stream.getTracks().forEach(track => track.stop());

		} catch (err) {
			error = 'Error accessing microphones: ' + (err instanceof Error ? err.message : 'Unknown error');
		}

		// Detect pointer devices (basic detection)
		detectPointerDevices();
		
		// Detect keyboards (basic detection)
		detectKeyboards();
		
		loading = false;
	}

	function detectPointerDevices() {
		const devices = [];
		
		// Check for mouse
		if (window.matchMedia('(pointer: fine)').matches) {
			devices.push('Mouse/Trackpad (fine pointer)');
		}
		
		// Check for touch
		if (window.matchMedia('(pointer: coarse)').matches) {
			devices.push('Touch screen (coarse pointer)');
		}

		// Check for multiple pointer types
		if ('ontouchstart' in window) {
			devices.push('Touch support detected');
		}

		pointerDevices = devices.length > 0 ? devices : ['No pointer devices detected'];
	}

	function detectKeyboards() {
		const devices = [];
		
		// Basic keyboard detection
		if (navigator.maxTouchPoints > 0) {
			devices.push('Virtual keyboard available (touch device)');
		} else {
			devices.push('Physical keyboard assumed (desktop)');
		}

		// Check for specific keyboard events support
		devices.push('Keyboard events supported: ' + ('KeyboardEvent' in window ? 'Yes' : 'No'));
		
		keyboards = devices;
	}

	async function testMicrophone(deviceId: string) {
		try {
			// Stop any existing stream
			if (currentStream) {
				currentStream.getTracks().forEach(track => track.stop());
			}

			if (activeMic === deviceId) {
				// Stop testing this mic
				activeMic = null;
				currentStream = null;
				if (audioContext) {
					audioContext.close();
					audioContext = null;
				}
				return;
			}

			// Start testing the selected mic
			const stream = await navigator.mediaDevices.getUserMedia({
				audio: { deviceId: { exact: deviceId } }
			});

			currentStream = stream;
			activeMic = deviceId;

			// Setup audio analysis
			audioContext = new AudioContext();
			analyser = audioContext.createAnalyser();
			analyser.fftSize = 256;

			const source = audioContext.createMediaStreamSource(stream);
			source.connect(analyser);

			// Start monitoring audio levels
			monitorAudioLevel(deviceId);

		} catch (err) {
			error = 'Error testing microphone: ' + (err instanceof Error ? err.message : 'Unknown error');
		}
	}

	function monitorAudioLevel(deviceId: string) {
		if (!analyser || activeMic !== deviceId) return;

		const bufferLength = analyser.frequencyBinCount;
		const dataArray = new Uint8Array(bufferLength);

		function updateLevel() {
			if (!analyser || activeMic !== deviceId) return;
			
			analyser.getByteFrequencyData(dataArray);
			
			// Calculate average volume
			const sum = dataArray.reduce((acc, val) => acc + val, 0);
			const average = sum / bufferLength;
			const normalizedLevel = Math.min(100, (average / 255) * 100);
			
			audioLevels = { ...audioLevels, [deviceId]: normalizedLevel };
			
			requestAnimationFrame(updateLevel);
		}
		
		updateLevel();
	}

	// Run detection on mount
	$effect(() => {
		detectDevices();

		// Cleanup on unmount
		return () => {
			if (currentStream) {
				currentStream.getTracks().forEach(track => track.stop());
			}
			if (audioContext) {
				audioContext.close();
			}
		};
	});
</script>

<main class="test-devices">
	<h1>Device Testing Page</h1>
	<p class="subtitle">Hidden page for testing device enumeration</p>

	{#if loading}
		<div class="loading">Loading devices...</div>
	{:else}
		{#if error}
			<div class="error">{error}</div>
		{/if}

		<section class="device-section">
			<h2>🎤 Microphones ({microphones.length})</h2>
			<ul class="device-list">
				{#each microphones as mic, index}
					<li class="device-item" class:active={activeMic === mic.deviceId}>
						<div class="device-info">
							<div class="device-name">{mic.label || `Microphone ${index + 1}`}</div>
							<div class="device-details">ID: {mic.deviceId}</div>
						</div>
						<div class="device-controls">
							<div class="audio-visualizer">
								<div class="level-bar">
									<div 
										class="level-fill" 
										style="width: {audioLevels[mic.deviceId] || 0}%"
									></div>
								</div>
								<span class="level-text">{Math.round(audioLevels[mic.deviceId] || 0)}%</span>
							</div>
							<button 
								class="test-btn" 
								class:active={activeMic === mic.deviceId}
								onclick={() => testMicrophone(mic.deviceId)}
							>
								{activeMic === mic.deviceId ? 'Stop' : 'Test'}
							</button>
						</div>
					</li>
				{/each}
			</ul>
		</section>

		<section class="device-section">
			<h2>🖱️ Pointer Devices ({pointerDevices.length})</h2>
			<ul class="device-list">
				{#each pointerDevices as device}
					<li class="device-item">
						<div class="device-name">{device}</div>
					</li>
				{/each}
			</ul>
		</section>

		<section class="device-section">
			<h2>⌨️ Keyboard Information ({keyboards.length})</h2>
			<ul class="device-list">
				{#each keyboards as keyboard}
					<li class="device-item">
						<div class="device-name">{keyboard}</div>
					</li>
				{/each}
			</ul>
		</section>

		<section class="device-section">
			<h2>🔄 Actions</h2>
			<button onclick={detectDevices} class="refresh-btn">Refresh Devices</button>
		</section>
	{/if}
</main>

<style>
	.test-devices {
		max-width: 1200px;
		margin: 0 auto;
		padding: 2rem;
		font-family: system-ui, -apple-system, sans-serif;
	}

	h1 {
		color: #333;
		margin-bottom: 0.5rem;
	}

	.subtitle {
		color: #666;
		margin-bottom: 2rem;
		font-style: italic;
	}

	.loading {
		text-align: center;
		padding: 2rem;
		color: #666;
	}

	.error {
		background: #fee;
		border: 1px solid #fcc;
		border-radius: 4px;
		padding: 1rem;
		margin-bottom: 1rem;
		color: #c33;
	}

	.device-section {
		margin-bottom: 2rem;
		border: 1px solid #ddd;
		border-radius: 8px;
		padding: 1.5rem;
	}

	.device-section h2 {
		margin: 0 0 1rem 0;
		color: #444;
		font-size: 1.25rem;
	}

	.device-list {
		list-style: none;
		padding: 0;
		margin: 0;
	}

	.device-item {
		padding: 1rem;
		border-bottom: 1px solid #eee;
		background: #fafafa;
		margin-bottom: 0.5rem;
		border-radius: 4px;
		display: flex;
		justify-content: space-between;
		align-items: center;
		transition: all 0.2s ease;
	}

	.device-item.active {
		background: #e6f3ff;
		border-left: 4px solid #0066cc;
	}

	.device-item:last-child {
		border-bottom: none;
	}

	.device-info {
		flex: 1;
	}

	.device-name {
		font-weight: 600;
		color: #333;
	}

	.device-details {
		font-size: 0.875rem;
		color: #666;
		margin-top: 0.25rem;
		font-family: monospace;
		word-break: break-all;
		max-width: 400px;
	}

	.device-controls {
		display: flex;
		align-items: center;
		gap: 1rem;
	}

	.audio-visualizer {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		min-width: 120px;
	}

	.level-bar {
		width: 80px;
		height: 8px;
		background: #ddd;
		border-radius: 4px;
		overflow: hidden;
	}

	.level-fill {
		height: 100%;
		background: linear-gradient(90deg, #4ade80 0%, #eab308 70%, #ef4444 100%);
		transition: width 0.1s ease;
		border-radius: 4px;
	}

	.level-text {
		font-size: 0.75rem;
		color: #666;
		min-width: 30px;
		text-align: right;
	}

	.test-btn {
		background: #0066cc;
		color: white;
		border: none;
		padding: 0.5rem 1rem;
		border-radius: 4px;
		cursor: pointer;
		font-size: 0.875rem;
		min-width: 60px;
		transition: background 0.2s ease;
	}

	.test-btn:hover {
		background: #0052a3;
	}

	.test-btn.active {
		background: #dc2626;
	}

	.test-btn.active:hover {
		background: #b91c1c;
	}

	.refresh-btn {
		background: #0066cc;
		color: white;
		border: none;
		padding: 0.75rem 1.5rem;
		border-radius: 4px;
		cursor: pointer;
		font-size: 1rem;
	}

	.refresh-btn:hover {
		background: #0052a3;
	}
</style>