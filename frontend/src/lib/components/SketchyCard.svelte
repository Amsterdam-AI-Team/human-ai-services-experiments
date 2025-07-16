<script>
	let {
		logo = "/images/wallet.svg",
		linkText = "Parkeerboete betalen",
		href = "#",
	} = $props();
</script>

<div class="sketchy-card">
	<img src="/images/card-border-sketchy.svg" alt="" class="card-border" />

	<div class="card-content">
		<div class="icon-container">
			<img src={logo} alt="" class="icon" />
		</div>

		<a {href} class="card-link">
			{linkText}
			<img src="/images/chevron-right.svg" alt="" class="chevron" />
		</a>
	</div>
</div>

<style>
	.sketchy-card {
		position: relative;
		display: inline-block;
		width: 280px;
		/* height: 200px; */
	}

	.card-border {
		position: absolute;
		top: 0;
		left: 0;
		width: 100%;
		height: 100%;
		object-fit: fill;
		z-index: 1;
	}

	.card-content {
		position: relative;
		z-index: 2;
		padding: 32px 24px;
		height: 100%;
		display: flex;
		flex-direction: column;
		justify-content: flex-start;
		align-items: flex-start;
		box-sizing: border-box;
		gap: .5rem;
	}

	.icon-container {
		display: flex;
		align-items: center;
		justify-content: flex-start;
	}
	
	.icon {
		width: 20px;
		height: 20px;
		object-fit: contain;
	}
	
	.card-link {
		color: #004699;
		text-decoration: underline;
		text-underline-offset: 0.25em;
		font-family: "Amsterdam Sans";
		font-weight: 400;
		font-size: 1.125rem;
		line-height: 1.2;
		transition: color 0.1s ease;
		text-align: left;
		align-self: flex-start;
		display: flex;
		align-items: center;
		gap: 0.1rem;
	}

	.card-link:hover {
		color: #0066cc;
	}

	.chevron {
		width: 1.4rem;
		height: 1.4rem;
		object-fit: contain;
	}
</style>
