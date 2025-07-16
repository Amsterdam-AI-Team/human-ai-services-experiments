<!-- CalloutBubble.svelte -->
<script>
	let { text = '' } = $props();
</script>

<div class="callout-bubble">
	<svg
		class="bubble-svg"
		width="519"
		height="154"
		viewBox="0 0 519 154"
		fill="none"
		xmlns="http://www.w3.org/2000/svg"
	>
		<path
			d="M3.58427 2.88823C164.929 5.89585 326.189 6.22708 515.752 2.97435M2.93365 3.86206C166.651 4.1138 330.867 4.27942 516.43 3.35859M517.479 5.76335C517.782 31.5997 517.047 65.2466 517.137 129.672M516.817 2.74911C516.492 30.4934 516.397 58.7743 516.06 132.786M515.269 131.951C449.952 132.824 387.392 135.457 278.653 135.302M2.45689 131.547C107.729 132.143 192.629 134.82 259.207 135.237L268.611 150.515M516.273 132.434C437.088 134.423 361.621 135.397 278.653 135.302M2.87195 131.606C95.5579 133.863 177.553 135.108 259.247 135.302M3.01778 131.5C1.89601 84.8226 2.92243 36.5947 1.83431 1.4043M3.89276 130.772C1.34073 88.1615 1.03224 46.0813 2.36154 4.00118M268.611 150.515C268.611 150.515 278.457 135.6 278.653 135.302M268.611 150.515L278.653 135.302M268.611 150.515C268.611 150.515 261.377 135.307 259.247 135.302M268.611 150.515L259.247 135.302M268.611 150.515C268.611 150.515 276.723 135.3 278.653 135.302"
			stroke="#1864AB"
			stroke-width="2.7"
			stroke-linecap="round"
		/>
	</svg>
	<div class="bubble-content">
		{text}
	</div>
</div>

<style>
	@import url('https://fonts.googleapis.com/css2?family=Patrick+Hand&display=swap');
	.callout-bubble {
		position: relative;
		max-width: 519px;
		margin: 0 auto 0 auto;
		transform: translateX(-11px);
	}

	.bubble-svg {
		width: 100%;
		height: auto;
	}

	.bubble-content {
		position: absolute;
		top: 0;
		left: 0;
		right: 0;
		bottom: 20px;
		display: flex;
		align-items: center;
		justify-content: center;
		font-family: 'Patrick Hand', cursive;
		font-size: 1.75rem;
		line-height: 1;
		text-align: center;
		padding: 20px 40px;
		color: #000;
	}
</style>
