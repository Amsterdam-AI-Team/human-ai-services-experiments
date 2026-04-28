import { json } from "@sveltejs/kit";

/**
 * No-op feedback endpoint. The demo has a no-PII-persistence requirement:
 * feedback content is acknowledged but not stored.
 *
 * @type {import("./$types").RequestHandler}
 */
export async function POST() {
	return json({ status: "ok" });
}
