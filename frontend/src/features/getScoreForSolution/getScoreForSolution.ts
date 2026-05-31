import { API_V1_BASE_URL } from "@/shared/api/config";
import { getErrorMessage } from "@/shared/api/getErrorMessage";

type SubmissionCheckDetail = {
	name: string;
	status: string;
};

type SubmissionCheckReport = {
	total?: number;
	passed?: number;
	failed?: number;
	details?: SubmissionCheckDetail[];
};

export type SubmissionInfo = {
	id: number;
	taskId: number;
	userId: number;
	language: string;
	status: string;
	score: number | null;
	submittedAt: string;
	checkedAt: string | null;
	memoryUsedKb: number | null;
	executionTimeMs: number | null;
};

export type SubmissionCheck = {
	id: number;
	checkType: string;
	status: string;
	score: number;
	report: SubmissionCheckReport;
	createdAt: string;
};

export type SolutionResultsProps = {
	submission: SubmissionInfo;
	checks: SubmissionCheck[];
	totalTests: number;
	testsPassed: number;
	failedTests: number;
	overallScore: number;
};

export async function getScore(
	submissionId: number,
): Promise<SolutionResultsProps> {
	const [submissionResponse, checksResponse] = await Promise.all([
		fetch(`${API_V1_BASE_URL}/submissions/${submissionId}`, {
			method: "GET",
			credentials: "include",
		}),
		fetch(`${API_V1_BASE_URL}/submissions/${submissionId}/checks`, {
			method: "GET",
			credentials: "include",
		}),
	]);

	if (!submissionResponse.ok) {
		throw new Error(
			await getErrorMessage(
				submissionResponse,
				"Failed to fetch submission result",
			),
		);
	}

	if (!checksResponse.ok) {
		throw new Error(
			await getErrorMessage(
				checksResponse,
				"Failed to fetch submission checks",
			),
		);
	}

	const submission = (await submissionResponse.json()) as SubmissionInfo;
	const checks = (await checksResponse.json()) as SubmissionCheck[];
	const testsCheck = checks.find((check) => check.checkType === "tests");
	const totalTests = testsCheck?.report.total ?? 0;
	const testsPassed = testsCheck?.report.passed ?? 0;

	return {
		submission,
		checks,
		totalTests,
		testsPassed,
		failedTests: Math.max(totalTests - testsPassed, 0),
		overallScore: submission.score ?? testsCheck?.score ?? 0,
	};
}
