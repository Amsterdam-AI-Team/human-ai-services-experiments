<script>
	let { logo = '/images/wallet.svg', linkText = 'Parkeerboete betalen', href = '#' } = $props();
</script>

<div class="sketchy-card">
	<img src="/images/card-border-sketchy.svg" alt="" class="card-border" />
	
	<div class="card-content">
		<div class="logo-container">
			<img src={logo} alt="" class="logo" />
		</div>
		
		<a {href} class="card-link">
			{linkText}
			<img src="/images/chevron-left.svg" alt="" class="chevron" />
		</a>
	</div>
</div>

<style>
	.sketchy-card {
		position: relative;
		display: inline-block;
		width: 280px;
		height: 200px;
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
		justify-content: space-between;
		align-items: center;
		box-sizing: border-box;
	}

	.logo-container {
		flex: 1;
		display: flex;
		align-items: center;
		justify-content: center;
	}

	.logo {
		width: 64px;
		height: 64px;
		object-fit: contain;
	}

	.card-link {
		display: flex;
		align-items: center;
		gap: 8px;
		color: #004699;
		text-decoration: none;
		font-family: 'Amsterdam Sans';
		font-weight: 400;
		font-size: 1.125rem;
		line-height: 1.2;
		transition: color 0.1s ease;
	}

	.card-link:hover {
		color: #0066cc;
	}

	.chevron {
		width: 16px;
		height: 16px;
		transform: rotate(180deg);
		transition: transform 0.1s ease;
	}

	.card-link:hover .chevron {
		transform: rotate(180deg) translateX(2px);
	}
</style>