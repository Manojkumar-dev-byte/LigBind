import axios from "axios";

const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

export const api = axios.create({
	baseURL: apiBaseUrl,
	headers: {
		"Content-Type": "application/json",
	},
});

export async function rankProteinTarget(payload) {
	const response = await api.post("/predict/rank", payload);
	return response.data;
}

export async function downloadRankingsCsv(payload) {
	const response = await api.post("/predict/csv", payload, {
		responseType: "blob",
	});

	return response.data;
}
