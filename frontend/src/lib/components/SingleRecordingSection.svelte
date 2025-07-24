<!-- SingleRecordingSection.svelte -->
<script lang="ts">
	import { sendToEndpoint, type EndpointType } from "$lib/utils/apiHelpers";
	import { addApiResponse } from "$lib/stores/apiStore";
	import { getSessionId } from "$lib/stores/sessionStore";

	let {
		endpoint = "analyze" as EndpointType,
		intentcode = null,
		recordKey = "e",
	} = $props();

	let isAnalyzing = $state(false);
	let isRecording = $state(false);
	let mediaRecorder = $state<MediaRecorder | null>(null);
	let audioChunks = $state<Blob[]>([]);
	let keyPressed = $state(false);
	let keyPressTimer = $state<number | null>(null);
	let isHoldToTalk = $state(false);

	async function handleRecordingStop(audioBlob: Blob) {
		// Send audio to the specified endpoint
		isAnalyzing = true;
		const formData = new FormData();

		// TODO: API inconsistency - different endpoints expect different field names
		// analyze endpoint expects 'file', chat/yap endpoints expect 'audio'
		// When API becomes consistent, this can be simplified to always use the same field name
		const audioFieldName = endpoint === "analyze" ? "file" : "audio";
		formData.append(audioFieldName, audioBlob, "recording.wav");

		// Add intentcode to FormData if provided
		if (intentcode) {
			formData.append("intentcode", intentcode);
		}

		// Add session_id to FormData if it exists and endpoint is chat (using FormData mode)
		if (endpoint === "chat") {
			const currentSessionId = getSessionId();
			if (currentSessionId) {
				formData.append("session_id", currentSessionId);
			}
		}

		try {
			const result = await sendToEndpoint(endpoint, formData);
			console.log("API response:", result);

			// Store the response in the store
			addApiResponse(endpoint, result);
		} catch (error) {
			console.error("API error:", error);
			// Store error in the store as well
			addApiResponse(endpoint, {
				error: error instanceof Error ? error.message : "Unknown error",
			});
		} finally {
			isAnalyzing = false;
		}
	}

	async function startRecording() {
		if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
			try {
				const stream = await navigator.mediaDevices.getUserMedia({
					audio: true,
				});
				mediaRecorder = new MediaRecorder(stream);
				mediaRecorder.start();
				isRecording = true;
				audioChunks = [];

				mediaRecorder.addEventListener("dataavailable", (event) => {
					audioChunks.push(event.data);
				});

				mediaRecorder.addEventListener("stop", async () => {
					const audioBlob = new Blob(audioChunks, {
						type: "audio/wav",
					});
					console.log("Recording stopped", audioBlob);
					audioChunks = [];
					isRecording = false;

					// Handle the stopped recording
					await handleRecordingStop(audioBlob);
				});
			} catch (error) {
				console.error("Error accessing microphone:", error);
			}
		}
	}

	async function stopRecording() {
		if (mediaRecorder && mediaRecorder.state !== "inactive") {
			mediaRecorder.stop();
			mediaRecorder.stream.getTracks().forEach((track) => track.stop());
		}
	}

	async function toggleRecording() {
		if (isRecording) {
			await stopRecording();
		} else {
			await startRecording();
		}
	}

	function handleKeyDown(event: KeyboardEvent) {
		if (
			event.key.toLowerCase() === recordKey.toLowerCase() &&
			!keyPressed &&
			!isAnalyzing
		) {
			keyPressed = true;

			// Start timer for distinguishing between short press and hold
			keyPressTimer = window.setTimeout(() => {
				// Long press detected - start hold-to-talk
				isHoldToTalk = true;
				if (!isRecording) {
					startRecording();
				}
			}, 200); // 200ms threshold
		}
	}

	function handleKeyUp(event: KeyboardEvent) {
		if (event.key.toLowerCase() === recordKey.toLowerCase() && keyPressed) {
			keyPressed = false;

			if (keyPressTimer) {
				clearTimeout(keyPressTimer);
				keyPressTimer = null;
			}

			if (isHoldToTalk) {
				// End hold-to-talk
				isHoldToTalk = false;
				if (isRecording) {
					stopRecording();
				}
			} else {
				// Short press - toggle recording
				toggleRecording();
			}
		}
	}

	// Add keyboard event listeners when component mounts
	$effect(() => {
		window.addEventListener("keydown", handleKeyDown);
		window.addEventListener("keyup", handleKeyUp);

		return () => {
			window.removeEventListener("keydown", handleKeyDown);
			window.removeEventListener("keyup", handleKeyUp);
		};
	});
</script>

<div class="recording-section">
	<!-- <p>{displayText}</p> -->
	<div class="button-container">
		<button
			class="record-button"
			onclick={toggleRecording}
			class:recording={isRecording}
			class:analyzing={isAnalyzing}
			class:keyboard-active={keyPressed}
			disabled={isAnalyzing}
		>
			<img
				src={isRecording
					? "/images/record-button-stop.svg"
					: isAnalyzing
						? "/images/record-button-empty.svg"
						: "/images/record-button.svg"}
				alt="Record button"
			/>

			<!-- Squiggly overlay that appears when analyzing -->
			<svg
				class="squiggly-overlay"
				viewBox="0 0 90 90"
				fill="none"
				xmlns="http://www.w3.org/2000/svg"
			>
				<path
					class="squiggly-path path1"
					d="M14 58.4907C14 57.7389 14 56.5999 14.1879 55.1791C14.5863 52.1675 19.8658 51.2809 22.5339 50.5206C23.6856 50.1924 25.0026 49.9483 26.3296 50.2302C28.783 50.7514 28.6132 54.8687 29.3735 57.3431C29.7252 58.4879 30.3217 59.624 31.361 60.4782C32.6197 61.5127 34.4961 60.3928 35.6322 59.6354C36.7684 58.8779 37.7251 57.9269 38.3886 56.7907C39.6785 54.5819 39.4336 51.6681 40.8545 49.5752C41.198 49.0693 41.8938 49.0029 42.4662 49C43.6173 48.9943 44.747 49.5667 45.7892 50.1333C48.109 51.3946 48.5455 54.4928 49.3058 56.7736C50.0869 59.117 51.393 60.763 52.2444 61.5232C52.6282 61.8659 53.2837 61.5318 53.7621 61.1531C55.8324 59.5141 56.5185 56.7936 57.2787 54.5127C57.6574 53.3766 58.2269 52.2319 59.0783 51.1897C59.9295 50.1479 61.4503 49.9483 62.8712 50.1362C65.5108 50.4853 66.5757 53.9233 68.0023 56.2041C69.3327 58.3312 69.9984 60.1935 70.565 61.1417C70.8419 61.6049 71.5075 61.714 72.0799 61.6229C72.6522 61.5318 73.216 61.1559 73.6004 60.6804C73.9848 60.2048 74.1728 59.641 75.5054 57.9212"
				/>
				<path
					class="squiggly-path path2"
					d="M13.8506 35.6782C13.8506 34.9264 13.8506 33.7874 14.0385 32.3666C14.4368 29.355 19.7164 28.4684 22.3845 27.7081C23.5362 27.3799 24.8532 27.1358 26.1801 27.4177C28.6336 27.9389 28.4638 32.0562 29.2241 34.5306C29.5758 35.6754 30.1723 36.8115 31.2116 37.6657C32.4703 38.7002 34.3467 37.5803 35.4828 36.8229C36.619 36.0654 37.5757 35.1144 38.2392 33.9782C39.529 31.7694 39.2842 28.8556 40.7051 26.7627C41.0486 26.2568 41.7444 26.1904 42.3168 26.1875C43.4679 26.1818 44.5976 26.7542 45.6398 27.3208C47.9595 28.5821 48.3961 31.6803 49.1564 33.9611C49.9375 36.3045 51.2436 37.9505 52.095 38.7107C52.4788 39.0534 53.1343 38.7193 53.6127 38.3406C55.683 36.7016 56.369 33.9811 57.1293 31.7002C57.508 30.5641 58.0775 29.4194 58.9289 28.3772C59.7801 27.3354 61.3009 27.1358 62.7218 27.3237C65.3614 27.6728 66.4263 31.1108 67.8529 33.3916C69.1833 35.5187 69.849 37.381 70.4156 38.3292C70.6924 38.7924 71.3581 38.9015 71.9305 38.8104C72.5028 38.7193 73.0666 38.3434 73.451 37.8679C73.8354 37.3923 74.0234 36.8285 75.356 35.1087"
				/>
			</svg>
		</button>
	</div>

	<!-- {#if keyPressed}
		<p class="keyboard-hint">Press '{recordKey.toUpperCase()}' to record • Hold for push-to-talk</p>
	{/if} -->
</div>

<style>
	.recording-section {
		display: flex;
		flex-direction: column;
		align-items: center;
		gap: 1rem;
		width: 100%;
		justify-content: center;
	}

	.button-container {
		display: flex;
		align-items: center;
		justify-content: center;
	}

	.record-button {
		background: none;
		border: none;
		cursor: pointer;
		transition: transform 0.2s;
		padding: 0;
		position: relative;
	}

	.record-button:hover {
		transform: scale(1.05);
	}

	.record-button.recording {
		animation: pulse 1s infinite;
	}

	.record-button.keyboard-active {
		transform: scale(1.05);
		box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.5);
		border-radius: 50%;
	}

	.record-button img {
		width: 100px;
		height: 100px;
	}

	@keyframes pulse {
		0% {
			transform: scale(1);
		}
		50% {
			transform: scale(1.1);
		}
		100% {
			transform: scale(1);
		}
	}

	.keyboard-hint {
		margin-top: 1rem;
		font-size: 0.875rem;
		color: #666;
		text-align: center;
	}

	.squiggly-overlay {
		position: absolute;
		top: 50%;
		left: 50%;
		transform: translate(-50%, -50%);
		pointer-events: none;
		opacity: 0;
		transition: opacity 0.3s ease;
		width: 90px;
		height: 90px;
	}

	.record-button.analyzing .squiggly-overlay {
		opacity: 1;
	}

	/* Squiggly path animations */
	.squiggly-path {
		stroke: #1864ab;
		stroke-width: 2;
		stroke-linecap: round;
		fill: none;
	}

	.squiggly-path.path1 {
		animation:
			draw-line 3s infinite,
			wiggle 2s infinite,
			pulse-stroke 1.5s infinite;
	}

	.squiggly-path.path2 {
		animation:
			draw-line 3s infinite,
			wiggle-reverse 2s infinite,
			pulse-stroke-reverse 1.5s infinite;
	}

	@keyframes draw-line {
		0% {
			stroke-dasharray: 0 200;
		}
		50% {
			stroke-dasharray: 100 100;
		}
		100% {
			stroke-dasharray: 0 200;
		}
	}

	@keyframes wiggle {
		0%,
		100% {
			transform: translate(0, 0);
		}
		25% {
			transform: translate(1px, -0.5px);
		}
		50% {
			transform: translate(0, 0);
		}
		75% {
			transform: translate(-1px, 0.5px);
		}
	}

	@keyframes wiggle-reverse {
		0%,
		100% {
			transform: translate(0, 0);
		}
		25% {
			transform: translate(-1px, 0.5px);
		}
		50% {
			transform: translate(0, 0);
		}
		75% {
			transform: translate(1px, -0.5px);
		}
	}

	@keyframes pulse-stroke {
		0%,
		100% {
			stroke-width: 2;
		}
		25% {
			stroke-width: 2.5;
		}
		50% {
			stroke-width: 2;
		}
		75% {
			stroke-width: 1.5;
		}
	}

	@keyframes pulse-stroke-reverse {
		0%,
		100% {
			stroke-width: 2;
		}
		25% {
			stroke-width: 1.5;
		}
		50% {
			stroke-width: 2;
		}
		75% {
			stroke-width: 2.5;
		}
	}
</style>
