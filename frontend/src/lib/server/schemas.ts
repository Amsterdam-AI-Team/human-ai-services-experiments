import { z, type ZodObject } from "zod";
import slugify from "slugify";
import type { Intent } from "./i18n";

export type StepSchema = ZodObject<Record<string, z.ZodTypeAny>>;

export interface StepShape {
	draft: string;
	vragen: string[];
	[key: string]: unknown;
}

export function buildStepSchema(intent: Intent): StepSchema {
	const shape: Record<string, z.ZodTypeAny> = {
		draft: z.string().default("").describe("Running draft of the output document."),
	};
	for (const step of intent.steps) {
		const key = slugify(step.title, { lower: true });
		shape[key] = z.boolean().default(false).describe(step.title);
	}
	shape.vragen = z.array(z.string()).default([]).describe("Follow-up questions");
	return z.object(shape);
}

export const BurgerTurnSchema = z.object({
	message: z.string().describe("Antwoord van de burger"),
});
export type BurgerTurn = z.infer<typeof BurgerTurnSchema>;

export const GemeenteTurnSchema = z.object({
	finished: z.boolean().default(false).describe("Akkoord bereikt?"),
	message: z.string().describe("Openstaande vragen, regels gescheiden door \\n"),
	draft: z.string().nullable().optional().describe("Definitieve samenvatting of concept-tekst"),
});
export type GemeenteTurn = z.infer<typeof GemeenteTurnSchema>;
