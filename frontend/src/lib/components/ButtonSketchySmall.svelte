<script>
	let { text = 'Button', disabled = false, onclick } = $props();

	function handleClick(event) {
		if (!disabled && onclick) {
			onclick(event);
		}
	}
</script>

<button
	class="svg-button"
	onclick={handleClick}
	{disabled}
>
	<svg
		width="218"
		height="52"
		viewBox="0 0 218 52"
		fill="none"
		xmlns="http://www.w3.org/2000/svg"
		class="button-svg"
	>
		<path
			d="M5.14489 2.8144C87.4621 1.90053 168.315 1.32237 215.039 3.97073L5.14489 2.8144ZM3.58019 2.72426C46.8573 3.9987 91.7302 4.0702 215.334 3.65367L3.58019 2.72426ZM213.351 3.60394C216.976 13.0038 216.72 22.5559 213.56 49.4995L213.351 3.60394ZM215.039 2.64966C213.444 18.9999 213.049 34.3088 213.056 48.7535L215.039 2.64966ZM214.497 48.5515C170.004 49.6488 129.469 49.5555 2 47.9578L214.497 48.5515ZM215.28 49.3193C130.313 48.2562 46.6869 48.1505 4.6414 48.9027L215.28 49.3193ZM2.31759 50C2.81333 31.8842 5.35404 13.8119 5.68712 2L2.31759 50ZM4.55619 48.6634C3.59569 33.1151 2.67391 18.7325 5.15264 2.69628L4.55619 48.6634Z"
			fill="#004699"
		/>
		<path
			d="M5.14489 2.8144C87.4621 1.90053 168.315 1.32237 215.039 3.97073M3.58019 2.72426C46.8573 3.9987 91.7302 4.0702 215.334 3.65367M213.351 3.60394C216.976 13.0038 216.72 22.5559 213.56 49.4995M215.039 2.64966C213.444 18.9999 213.049 34.3088 213.056 48.7535M214.497 48.5515C170.004 49.6488 129.469 49.5555 2 47.9578M215.28 49.3193C130.313 48.2562 46.6869 48.1505 4.6414 48.9027M2.31759 50C2.81333 31.8842 5.35404 13.8119 5.68712 2M4.55619 48.6634C3.59569 33.1151 2.67391 18.7325 5.15264 2.69628"
			stroke="#004699"
			stroke-width="2.7"
			stroke-linecap="round"
		/>
		<path
			d="M3.36743 27.8496L5.54092 3.14648L214.668 3.97007L212.977 48.5729H129.906H3.36743V27.8496Z"
			fill="#004699"
		/>
	</svg>

	<span class="button-text">{text}</span>
</button>

<style>
	.svg-button {
		position: relative;
		border: none;
		padding: 0;
		background: transparent;
		cursor: pointer;
		transition: transform 0.1s ease;
		outline: none;
		width: 218px;
		height: 52px;
	}

	.svg-button:disabled {
		cursor: not-allowed;
		opacity: 0.6;
	}

	.button-svg {
		width: 100%;
		height: 100%;
		display: block;
		transition: filter 0.1s ease;
	}

	.button-text {
		position: absolute;
		top: 50%;
		left: 50%;
		transform: translate(-50%, -50%);
		color: white;
		font-size: 1rem;
		white-space: nowrap;
		pointer-events: none;
		z-index: 10;
		line-height: 1;
		font-family: 'Amsterdam Sans';
		font-weight: 200;
	}

	.svg-button:hover:not(:disabled) {
		transform: translateY(-2px);
	}

	.svg-button:hover:not(:disabled) .button-svg {
		filter: brightness(1.1);
	}

	.svg-button:active:not(:disabled) {
		transform: translateY(0px);
	}

	.svg-button:active:not(:disabled) .button-svg {
		filter: brightness(0.95);
	}

	.svg-button:focus {
		box-shadow: 0 0 0 3px rgba(0, 70, 153, 0.3);
	}

	.svg-button:disabled .button-svg {
		filter: grayscale(100%) brightness(0.8);
	}

	.svg-button:disabled .button-text {
		color: #ccc;
	}
</style>