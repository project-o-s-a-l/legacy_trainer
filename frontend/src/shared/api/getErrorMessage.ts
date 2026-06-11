type ErrorPayload = {
	detail?: string | Array<{ msg?: string }>;
	message?: string;
};

export async function getErrorMessage(
	response: Response,
	fallbackMessage: string,
): Promise<string> {
	try {
		const data = (await response.clone().json()) as ErrorPayload;

		if (typeof data.message === "string" && data.message.trim()) {
			return data.message;
		}

		if (typeof data.detail === "string" && data.detail.trim()) {
			return data.detail;
		}

		if (Array.isArray(data.detail)) {
			const validationMessage = data.detail
				.map((item) => item.msg?.trim())
				.filter(Boolean)
				.join(", ");

			if (validationMessage) {
				return validationMessage;
			}
		}
	} catch {
		// Ignore JSON parsing errors and fall back to text or a default message.
	}

	try {
		const text = await response.clone().text();
		if (text.trim()) {
			return text;
		}
	} catch {
		// Ignore text parsing errors and return the fallback below.
	}

	return fallbackMessage;
}
