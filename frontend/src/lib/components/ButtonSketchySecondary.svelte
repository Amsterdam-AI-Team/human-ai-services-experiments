<script>
	let { text = 'Terug', icon = '/images/back-arrow.svg', minWidth = '200px', height = '60px', disabled = false, onclick } = $props();

	function handleClick(event) {
		if (!disabled && onclick) {
			onclick(event);
		}
	}
</script>

<button
	class="svg-button"
	style="min-width: {minWidth}; height: {height};"
	onclick={handleClick}
	{disabled}
>
	<svg
		viewBox="0 0 233 91"
		preserveAspectRatio="none"
		xmlns="http://www.w3.org/2000/svg"
		class="button-svg"
	>
		<!-- Outer gray border -->
		<path
			d="M5.36533 3.48545C93.4524 1.81857 179.973 0.764015 229.972 5.59456M3.69095 3.32103C50.0016 5.64559 98.0197 5.77599 230.287 5.01626M228.165 4.92554C232.044 22.0706 231.771 39.4934 228.389 88.638M229.972 3.18496C228.265 33.0074 227.842 60.9304 227.85 87.2773M229.392 86.9088C181.78 88.9102 138.404 88.7401 2 85.8259M230.229 88.3092C139.307 86.3702 49.8192 86.1774 4.82655 87.5495M2.33985 89.5508C2.87034 56.5081 5.58913 23.5447 5.94556 2M4.73537 87.1129C3.70753 58.7533 2.72114 32.5198 5.37362 3.27"
			stroke="#004699"
			stroke-width="2.7"
			stroke-linecap="round"
			fill="none"
		/>

		<!-- Inner white fill -->
		<path
			d="M13.5406 11.1583C95.148 9.79387 175.304 8.93065 221.625 12.8848ZM11.9894 11.0237C54.8934 12.9265 99.3792 13.0333 221.917 12.4114ZM219.951 12.3371C223.545 26.3715 223.292 40.6332 220.158 80.8613ZM221.625 10.9123C220.043 35.3239 219.652 58.1808 219.659 79.7474ZM221.088 79.4458C176.978 81.084 136.793 80.9448 10.4229 78.5593ZM221.863 80.5921C137.63 79.0049 54.7244 78.8471 13.0415 79.9702ZM10.7377 81.6085C11.2292 54.5608 13.748 27.5781 14.0782 9.94238ZM12.957 79.6128C12.0048 56.3986 11.0909 34.9248 13.5483 10.982Z"
			fill="#ffffff"
		/>


		<!-- Main fill rectangle -->
		<path
			d="M11.7783 48.5361L13.9331 11.6533L221.256 12.883L219.581 79.4769H137.226H11.7783V48.5361Z"
			fill="#ffffff"
		/>
	</svg>

	<div class="button-content">
		<img src={icon} alt="" class="button-icon" />
		<span class="button-text">{text}</span>
	</div>
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
	}

	.svg-button:disabled {
		cursor: not-allowed;
		opacity: 0.6;
	}

	.button-svg {
		width: 80%;
		height: 80%;
		display: block;
		transition: filter 0.1s ease;
	}

	.button-content {
		position: absolute;
		top: 50%;
		left: 30%;
		transform: translate(-50%, -50%);
		display: flex;
		align-items: center;
		gap: 0.5rem;
		pointer-events: none;
		z-index: 10;
	}

	.button-icon {
		width: 48px;
		height: 48px;
		flex-shrink: 0;
	}

	.button-text {
		color: #004699;
		font-size: 1rem;
		white-space: nowrap;
		line-height: 1;
		font-family: 'Amsterdam Sans';
		font-weight: 500;
	}

	.svg-button:hover:not(:disabled) {
		transform: translateY(-1px);
	}

	.svg-button:hover:not(:disabled) .button-svg {
		filter: brightness(1.05);
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

	.svg-button:disabled .button-icon {
		filter: grayscale(100%) brightness(0.8);
	}
</style>