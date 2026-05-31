diff --git a/frontend/.gitignore b/frontend/.gitignore
index ca3d451..1a7eac9 100644
--- a/frontend/.gitignore
+++ b/frontend/.gitignore
@@ -1,4 +1,6 @@
 /.vite
+/dist
+/*.tsbuildinfo
 
 # Playwright
 node_modules/
diff --git a/frontend/package.json b/frontend/package.json
index 6e8a219..43ad0a8 100644
--- a/frontend/package.json
+++ b/frontend/package.json
@@ -16,7 +16,7 @@
     "test:e2e:report": "playwright show-report",
 
     "dev": "vite",
-    "build": "tsc -b && vite build",
+    "build": "tsc --noEmit -p tsconfig.app.json && vite build",
     "lint": "eslint .",
     "preview": "vite preview"
   },
diff --git a/frontend/src/app/App.tsx b/frontend/src/app/App.tsx
index 83050a7..7d501de 100644
--- a/frontend/src/app/App.tsx
+++ b/frontend/src/app/App.tsx
@@ -1,4 +1,4 @@
-import React, { useEffect, useMemo, useState } from "react";
+import { useEffect, useMemo, useState } from "react";
 import "./App.css";
 import { Navbar } from "@/widgets/index";
 import { Routes, useLocation } from "react-router-dom";
diff --git a/frontend/src/app/providers/router/routeConfig.ts b/frontend/src/app/providers/router/routeConfig.ts
index 61b9fe4..c5739aa 100644
--- a/frontend/src/app/providers/router/routeConfig.ts
+++ b/frontend/src/app/providers/router/routeConfig.ts
@@ -1,4 +1,3 @@
-import { CodeBlock } from "@/pages/CodeBlockPage/CodeBlock";
 import {
 	About,
 	Contact,
@@ -8,13 +7,13 @@ import {
 	Login,
 	Registration,
 	CodePage,
+	ForgotPassword,
 	CodeEditor,
 	ChooseTask,
 	Profile,
 	SolutionResult,
 } from "@/pages/index";
 
-import { ProfileImg } from "@/shared/index.ts";
 import type { AppPage } from "@/shared/index.ts";
 
 export const mainPageRoutes: AppPage[] = [
@@ -23,6 +22,7 @@ export const mainPageRoutes: AppPage[] = [
 		label: "About the company",
 		component: About,
 		showInNavbar: false,
+		showNavBar: true,
 		access: "public",
 	},
 	{
@@ -30,6 +30,7 @@ export const mainPageRoutes: AppPage[] = [
 		label: "Home",
 		component: Home,
 		showInNavbar: true,
+		showNavBar: true,
 		access: "public",
 	},
 	{
@@ -37,6 +38,7 @@ export const mainPageRoutes: AppPage[] = [
 		label: "Possibilites",
 		component: Possibilites,
 		showInNavbar: false,
+		showNavBar: true,
 		access: "public",
 	},
 	{
@@ -44,6 +46,7 @@ export const mainPageRoutes: AppPage[] = [
 		label: "Contact",
 		component: Contact,
 		showInNavbar: false,
+		showNavBar: true,
 		access: "public",
 	},
 	{
@@ -51,6 +54,7 @@ export const mainPageRoutes: AppPage[] = [
 		label: "Support",
 		component: Support,
 		showInNavbar: false,
+		showNavBar: true,
 		access: "public",
 	},
 	{
@@ -58,6 +62,7 @@ export const mainPageRoutes: AppPage[] = [
 		label: "Login",
 		component: Login,
 		showInNavbar: true,
+		showNavBar: true,
 		access: "guest",
 	},
 	{
@@ -65,6 +70,23 @@ export const mainPageRoutes: AppPage[] = [
 		label: "Registration",
 		component: Registration,
 		showInNavbar: true,
+		showNavBar: true,
+		access: "guest",
+	},
+	{
+		path: "/confirm-email",
+		label: "Confirm email",
+		component: CodePage,
+		showInNavbar: false,
+		showNavBar: true,
+		access: "guest",
+	},
+	{
+		path: "/forgot-password",
+		label: "Forgot password",
+		component: ForgotPassword,
+		showInNavbar: false,
+		showNavBar: true,
 		access: "guest",
 	},
 	{
@@ -72,34 +94,39 @@ export const mainPageRoutes: AppPage[] = [
 		label: "CodePage",
 		component: CodePage,
 		showInNavbar: false,
-		access: "private"
+		showNavBar: true,
+		access: "guest",
 	},
 	{
 		path: "/CodeBlock",
 		label: "CodeBlock",
 		component: CodeEditor,
 		showInNavbar: false,
-		access: "private"
+		showNavBar: false,
+		access: "private",
 	},
 	{
 		path: "/ChooseTask",
 		label: "ChooseTask",
 		component: ChooseTask,
 		showInNavbar: true,
-		access: "private"
+		showNavBar: true,
+		access: "private",
 	},
 	{
 		path: "/profile",
 		label: "Profile",
 		component: Profile,
 		showInNavbar: true,
-		access: "private"
+		showNavBar: true,
+		access: "private",
 	},
 	{
 		path: "/result",
 		label: "Solution Result",
 		component: SolutionResult,
-		showInNavbar: true,
-		access: "private"
-	}
+		showInNavbar: false,
+		showNavBar: true,
+		access: "private",
+	},
 ];
diff --git a/frontend/src/features/CheckSolution/CheckSolution.ts b/frontend/src/features/CheckSolution/CheckSolution.ts
index af1827a..c9fcfed 100644
--- a/frontend/src/features/CheckSolution/CheckSolution.ts
+++ b/frontend/src/features/CheckSolution/CheckSolution.ts
@@ -1,17 +1,21 @@
 import { API_V1_BASE_URL } from "@/shared/api/config";
+import { getErrorMessage } from "@/shared/api/getErrorMessage";
 
 export type CheckSolutionProps = {
-	ok: boolean;
+	submissionId: number;
+	taskId: number;
+	status: string;
+	score: number;
 	message: string;
 	testPassed: number;
 };
 
 export async function checkSolution(
+	taskId: number,
 	code: string,
 	language: string,
-	taskLevel: string,
 ): Promise<CheckSolutionProps> {
-	const response = await fetch(`${API_V1_BASE_URL}/submission/check`, {
+	const response = await fetch(`${API_V1_BASE_URL}/tasks/${taskId}/submit`, {
 		method: "POST",
 		headers: {
 			"Content-Type": "application/json",
@@ -21,10 +25,18 @@ export async function checkSolution(
 		body: JSON.stringify({
 			code,
 			language,
-			taskLevel,
 		}),
 	});
 
+	if (!response.ok) {
+		throw new Error(
+			await getErrorMessage(
+				response,
+				"Server error while checking solution",
+			),
+		);
+	}
+
 	let data: CheckSolutionProps | null = null;
 
 	try {
@@ -33,15 +45,9 @@ export async function checkSolution(
 		data = null;
 	}
 
-	if (!response.ok) {
-		throw new Error(
-			data?.message || "Server error while checking solution",
-		);
-	}
-
 	if (!data) {
-		throw new Error("Server can`t return solution score");
+		throw new Error("Server cannot return submission result");
 	}
 
 	return data;
-}
\ No newline at end of file
+}
diff --git a/frontend/src/features/getProfileInfo/getProfileInfo.ts b/frontend/src/features/getProfileInfo/getProfileInfo.ts
index 37f4703..93976ee 100644
--- a/frontend/src/features/getProfileInfo/getProfileInfo.ts
+++ b/frontend/src/features/getProfileInfo/getProfileInfo.ts
@@ -1,32 +1,53 @@
 import type { Profile } from "@/pages/ProfilePage/lib/profileInterface";
 import { API_V1_BASE_URL } from "@/shared/api/config";
+import { getErrorMessage } from "@/shared/api/getErrorMessage";
 
 export async function fetchProfileInfo(signal?: AbortSignal): Promise<Profile> {
-	const response = await fetch(`${API_V1_BASE_URL}/users/me`, {
-		method: "GET",
-		credentials: "include",
-		signal,
-	});
-	if (response.status === 401) {
+	const [profileResponse, progressResponse] = await Promise.all([
+		fetch(`${API_V1_BASE_URL}/users/me`, {
+			method: "GET",
+			credentials: "include",
+			signal,
+		}),
+		fetch(`${API_V1_BASE_URL}/users/me/progress`, {
+			method: "GET",
+			credentials: "include",
+			signal,
+		}),
+	]);
+
+	if (
+		profileResponse.status === 401 ||
+		progressResponse.status === 401
+	) {
 		throw new Error("Unauthorized");
 	}
 
-	if (!response.ok) {
-		throw new Error("Failed to fetch profile info");
+	if (!profileResponse.ok) {
+		throw new Error(
+			await getErrorMessage(
+				profileResponse,
+				"Failed to fetch profile info",
+			),
+		);
 	}
 
-	const profileInfo = await response.json();
+	const profileInfo = await profileResponse.json();
+	const progressInfo = progressResponse.ok
+		? await progressResponse.json()
+		: null;
+
 	return {
 		...profileInfo,
-		tasksCompleted: profileInfo.tasksCompleted ?? {
+		tasksCompleted: progressInfo?.tasksCompleted ?? {
 			easy: 0,
 			medium: 0,
 			hard: 0,
 		},
-		averageGrade: profileInfo.averageGrade ?? {
+		averageGrade: progressInfo?.averageGrade ?? {
 			easy: 0,
 			medium: 0,
-			hard: 0
+			hard: 0,
 		},
 	};
 }
diff --git a/frontend/src/features/getScoreForSolution/getScoreForSolution.ts b/frontend/src/features/getScoreForSolution/getScoreForSolution.ts
index f2f0012..1097458 100644
--- a/frontend/src/features/getScoreForSolution/getScoreForSolution.ts
+++ b/frontend/src/features/getScoreForSolution/getScoreForSolution.ts
@@ -1,22 +1,93 @@
 import { API_V1_BASE_URL } from "@/shared/api/config";
+import { getErrorMessage } from "@/shared/api/getErrorMessage";
 
+type SubmissionCheckDetail = {
+	name: string;
+	status: string;
+};
+
+type SubmissionCheckReport = {
+	total?: number;
+	passed?: number;
+	failed?: number;
+	details?: SubmissionCheckDetail[];
+};
+
+export type SubmissionInfo = {
+	id: number;
+	taskId: number;
+	userId: number;
+	language: string;
+	status: string;
+	score: number | null;
+	submittedAt: string;
+	checkedAt: string | null;
+	memoryUsedKb: number | null;
+	executionTimeMs: number | null;
+};
+
+export type SubmissionCheck = {
+	id: number;
+	checkType: string;
+	status: string;
+	score: number;
+	report: SubmissionCheckReport;
+	createdAt: string;
+};
 
 export type SolutionResultsProps = {
-	Architecture: number;
-	CodeLogic: number;
-	Standards: number;
+	submission: SubmissionInfo;
+	checks: SubmissionCheck[];
+	totalTests: number;
+	testsPassed: number;
+	failedTests: number;
+	overallScore: number;
 };
 
+export async function getScore(
+	submissionId: number,
+): Promise<SolutionResultsProps> {
+	const [submissionResponse, checksResponse] = await Promise.all([
+		fetch(`${API_V1_BASE_URL}/submissions/${submissionId}`, {
+			method: "GET",
+			credentials: "include",
+		}),
+		fetch(`${API_V1_BASE_URL}/submissions/${submissionId}/checks`, {
+			method: "GET",
+			credentials: "include",
+		}),
+	]);
 
-export async function getScore(): Promise<SolutionResultsProps>{
-	const response = await fetch(`${API_V1_BASE_URL}/submissions/score`, {
-		method: "GET",
-		credentials: "include",
-	});
+	if (!submissionResponse.ok) {
+		throw new Error(
+			await getErrorMessage(
+				submissionResponse,
+				"Failed to fetch submission result",
+			),
+		);
+	}
 
-	if(!response.ok) {
-		throw new Error("Failed to fetch score");
+	if (!checksResponse.ok) {
+		throw new Error(
+			await getErrorMessage(
+				checksResponse,
+				"Failed to fetch submission checks",
+			),
+		);
 	}
 
-	return response.json();
+	const submission = (await submissionResponse.json()) as SubmissionInfo;
+	const checks = (await checksResponse.json()) as SubmissionCheck[];
+	const testsCheck = checks.find((check) => check.checkType === "tests");
+	const totalTests = testsCheck?.report.total ?? 0;
+	const testsPassed = testsCheck?.report.passed ?? 0;
+
+	return {
+		submission,
+		checks,
+		totalTests,
+		testsPassed,
+		failedTests: Math.max(totalTests - testsPassed, 0),
+		overallScore: submission.score ?? testsCheck?.score ?? 0,
+	};
 }
diff --git a/frontend/src/features/getTask/getTask.ts b/frontend/src/features/getTask/getTask.ts
index 90c3f15..06fc680 100644
--- a/frontend/src/features/getTask/getTask.ts
+++ b/frontend/src/features/getTask/getTask.ts
@@ -1,4 +1,5 @@
 import { API_V1_BASE_URL } from "@/shared/api/config";
+import { getErrorMessage } from "@/shared/api/getErrorMessage";
 
 export type TaskResponse = {
 	id: number;
@@ -26,9 +27,8 @@ export async function getTask(
 	});
 
 	if (!response.ok) {
-		throw new Error("Get task failed");
+		throw new Error(await getErrorMessage(response, "Get task failed"));
 	}
 
 	return response.json();
 }
-
diff --git a/frontend/src/features/login/login-request.ts b/frontend/src/features/login/login-request.ts
index e13f21f..d50faf6 100644
--- a/frontend/src/features/login/login-request.ts
+++ b/frontend/src/features/login/login-request.ts
@@ -1,5 +1,6 @@
 import type { LoginResponse } from "@/shared";
 import { API_V1_BASE_URL } from "@/shared/api/config";
+import { getErrorMessage } from "@/shared/api/getErrorMessage";
 
 export async function login_request(
 	login: string,
@@ -19,7 +20,7 @@ export async function login_request(
 	});
 
 	if (!response.ok) {
-		throw new Error("Login failed");
+		throw new Error(await getErrorMessage(response, "Login failed"));
 	}
 
 	return response.json();
diff --git a/frontend/src/features/registr/registr-request.ts b/frontend/src/features/registr/registr-request.ts
index b295a45..624925e 100644
--- a/frontend/src/features/registr/registr-request.ts
+++ b/frontend/src/features/registr/registr-request.ts
@@ -1,5 +1,6 @@
 import type { RegisterResponse } from "@/shared";
 import { API_V1_BASE_URL } from "@/shared/api/config";
+import { getErrorMessage } from "@/shared/api/getErrorMessage";
 
 export async function register_request(
 	username: string,
@@ -19,18 +20,11 @@ export async function register_request(
 		}),
 	});
 
-	const responseText = await response.text();
-
 	if (!response.ok) {
-		console.error("REGISTER FAILED:", {
-			status: response.status,
-			statusText: response.statusText,
-			body: responseText,
-		});
-
 		throw new Error(
-			`Registration failed: ${response.status} ${response.statusText} ${responseText}`,
+			await getErrorMessage(response, "Registration failed"),
 		);
 	}
-  	return JSON.parse(responseText) as RegisterResponse;
+
+	return response.json() as Promise<RegisterResponse>;
 }
diff --git a/frontend/src/pages/CodeBlockPage/CodeBlock.tsx b/frontend/src/pages/CodeBlockPage/CodeBlock.tsx
index cd95dcd..d8e78b1 100644
--- a/frontend/src/pages/CodeBlockPage/CodeBlock.tsx
+++ b/frontend/src/pages/CodeBlockPage/CodeBlock.tsx
@@ -1,10 +1,9 @@
 import Editor, { useMonaco } from "@monaco-editor/react";
-import React, { useState, useEffect, useRef } from "react";
+import React, { useState, useEffect } from "react";
 import type { CodeBlockProps } from "./model/types.ts";
 import { BLUE_LIGHT_THEME_NAME, blueLightTheme } from "./lib/blueLightTheme.ts";
 import { Group, Panel, Separator } from "react-resizable-panels";
 import "./CodeBlock.css";
-import { useLocation } from "react-router-dom";
 
 export const CodeBlock: React.FC<CodeBlockProps> = ({
 	language = "javascript",
diff --git a/frontend/src/pages/CodeBlockPage/CodeEditor.tsx b/frontend/src/pages/CodeBlockPage/CodeEditor.tsx
index f1cc91f..487e00f 100644
--- a/frontend/src/pages/CodeBlockPage/CodeEditor.tsx
+++ b/frontend/src/pages/CodeBlockPage/CodeEditor.tsx
@@ -38,8 +38,8 @@ export default function CodeEditor() {
 	const RESULT_PANEL_MAX_HEIGHT = 380;
 
 	const monacoLanguage = chooseLanguage
-		? languageMap[chooseLanguage] || "plaintext"
-		: "plaintext";
+		? languageMap[chooseLanguage] || task?.language || "plaintext"
+		: task?.language || "plaintext";
 	const defaultCode = task?.legacyCode ?? "";
 
 	const [resultPanelHeight, setResultPanelHeight] = useState(
@@ -47,6 +47,7 @@ export default function CodeEditor() {
 	);
 	const [isResultPanelDragging, setIsResultPanelDragging] = useState(false);
 	const [isChecking, setIsChecking] = useState(false);
+	const [isLoadingResult, setIsLoadingResult] = useState(false);
 	const [checkResult, setCheckResult] = useState<CheckSolutionProps | null>(
 		null,
 	);
@@ -54,14 +55,29 @@ export default function CodeEditor() {
 	const [code, setCode] = useState(defaultCode);
 
 	const handleSubmit = async () => {
+		if (!task) {
+			const missingTaskResult: CheckSolutionProps = {
+				submissionId: 0,
+				taskId: 0,
+				status: "error",
+				score: 0,
+				message: "Please choose a task before submitting a solution",
+				testPassed: 0,
+			};
+
+			setCheckResult(missingTaskResult);
+			setResultPanelHeight(RESULT_PANEL_MAX_HEIGHT);
+
+			return null;
+		}
+
 		setIsChecking(true);
 		setCheckResult(null);
-
 		try {
 			const result = await checkSolution(
+				task.id,
 				code,
-				chooseLanguage as string,
-				chooseDificulty as string,
+				task.language || (chooseLanguage as string),
 			);
 
 			setCheckResult(result);
@@ -70,7 +86,10 @@ export default function CodeEditor() {
 			return result;
 		} catch (error) {
 			const result: CheckSolutionProps = {
-				ok: false,
+				submissionId: 0,
+				taskId: task.id,
+				status: "failed",
+				score: 0,
 				message:
 					error instanceof Error
 						? error.message
@@ -166,23 +185,45 @@ export default function CodeEditor() {
 					onClick={async () => {
 						const result = await handleSubmit();
 
-						if (!result || !result.ok) {
+						if (!result || result.status !== "passed") {
 							return;
 						}
 
-						const analysis = await getScore();
-
-						nav("/result", {
-							state: {
-								Architecture: analysis.Architecture,
-								CodeLogic: analysis.CodeLogic,
-								Standards: analysis.Standards,
-							},
-						});
+						try {
+							setIsLoadingResult(true);
+							const analysis = await getScore(result.submissionId);
+
+							nav("/result", {
+								state: {
+									result: analysis,
+									code,
+									taskTitle: task?.title,
+								},
+							});
+						} catch (error) {
+							setCheckResult({
+								submissionId: result.submissionId,
+								taskId: result.taskId,
+								status: "failed",
+								score: 0,
+								message:
+									error instanceof Error
+										? error.message
+										: "Failed to load submission result",
+								testPassed: result.testPassed,
+							});
+							setResultPanelHeight(RESULT_PANEL_MAX_HEIGHT);
+						} finally {
+							setIsLoadingResult(false);
+						}
 					}}
-					disabled={isChecking}
+					disabled={isChecking || isLoadingResult}
 				>
-					{isChecking ? "Checking..." : "Submit"}
+					{isChecking
+						? "Checking..."
+						: isLoadingResult
+							? "Loading result..."
+							: "Submit"}
 				</Button>
 				<button
 					type="button"
@@ -194,8 +235,8 @@ export default function CodeEditor() {
 			</div>
 			<div className="flex">
 				<span className="chosed-fields">
-					Language: {chooseLanguage || "not selected"}|Difficulty:{" "}
-					{chooseDificulty || "not selected"}
+					Language: {chooseLanguage || task?.language || "not selected"}
+					|Difficulty: {chooseDificulty || task?.difficulty || "not selected"}
 				</span>
 			</div>
 			<CodeBlock
@@ -212,7 +253,7 @@ export default function CodeEditor() {
 			{checkResult && (
 				<div
 					className={`check-result-bar ${
-						checkResult.ok
+						checkResult.status === "passed"
 							? "check-result-bar-success"
 							: "check-result-bar-error"
 					} ${isResultPanelDragging ? "check-result-bar-dragging" : ""}`}
@@ -226,7 +267,9 @@ export default function CodeEditor() {
 						onPointerCancel={handleResultPanelPointerUp}
 					>
 						<span className="check-result-title">
-							{checkResult.ok ? "Success" : "Error"}
+							{checkResult.status === "passed"
+								? "Success"
+								: "Error"}
 						</span>
 					</div>
 
@@ -236,7 +279,8 @@ export default function CodeEditor() {
 						</pre>
 
 						<div className="check-result-tests">
-							Tests passed: {checkResult.testPassed}
+							Tests passed: {checkResult.testPassed} | Score:{" "}
+							{checkResult.score}
 						</div>
 					</div>
 				</div>
diff --git a/frontend/src/pages/ForgotPasswordPage/ForgotPassword.css b/frontend/src/pages/ForgotPasswordPage/ForgotPassword.css
new file mode 100644
index 0000000..1772e6b
--- /dev/null
+++ b/frontend/src/pages/ForgotPasswordPage/ForgotPassword.css
@@ -0,0 +1,114 @@
+.forgot-password-page {
+	min-height: calc(100vh - 180px);
+	padding: 48px 24px 72px;
+	display: grid;
+	place-items: center;
+}
+
+.forgot-password-shell {
+	width: min(960px, 100%);
+	padding: 56px 64px;
+	gap: 42px;
+	box-shadow: var(--shadow-soft-lg);
+}
+
+.forgot-password-copy {
+	display: flex;
+	flex-direction: column;
+	gap: 14px;
+	max-width: 640px;
+}
+
+.forgot-password-kicker {
+	margin: 0;
+	font-size: 18px;
+	font-weight: 700;
+	letter-spacing: 0.08em;
+	text-transform: uppercase;
+	color: var(--btn-color-light-theme);
+}
+
+.forgot-password-title {
+	margin: 0;
+	font-size: clamp(42px, 6vw, 64px);
+	font-weight: 500;
+	line-height: 1.04;
+	color: var(--color-text-main);
+}
+
+.forgot-password-text {
+	margin: 0;
+	font-size: 22px;
+	line-height: 1.5;
+	color: var(--color-text-secondary);
+}
+
+.forgot-password-form {
+	display: flex;
+	flex-direction: column;
+	gap: 20px;
+	max-width: 520px;
+}
+
+.forgot-password-label {
+	font-size: 28px;
+	font-weight: 500;
+	color: var(--color-text-main);
+}
+
+.forgot-password-input {
+	max-width: none;
+	font-size: 28px;
+	padding: 22px 26px;
+}
+
+.forgot-password-actions {
+	display: flex;
+	align-items: center;
+	justify-content: space-between;
+	gap: 16px;
+	margin-top: 10px;
+}
+
+.forgot-password-submit {
+	min-width: 200px;
+}
+
+.forgot-password-link {
+	color: var(--btn-color-light-theme);
+	font-size: 20px;
+	text-decoration: none;
+}
+
+.forgot-password-link:hover {
+	color: var(--color-link-hover);
+}
+
+.forgot-password-error {
+	margin: 0;
+	font-size: 18px;
+	color: #b42318;
+}
+
+@media (max-width: 720px) {
+	.forgot-password-page {
+		padding-inline: 16px;
+	}
+
+	.forgot-password-shell {
+		padding: 36px 24px;
+	}
+
+	.forgot-password-actions {
+		flex-direction: column;
+		align-items: stretch;
+	}
+
+	.forgot-password-submit {
+		width: 100%;
+	}
+
+	.forgot-password-link {
+		text-align: center;
+	}
+}
diff --git a/frontend/src/pages/ForgotPasswordPage/ForgotPassword.tsx b/frontend/src/pages/ForgotPasswordPage/ForgotPassword.tsx
new file mode 100644
index 0000000..4f2dab7
--- /dev/null
+++ b/frontend/src/pages/ForgotPasswordPage/ForgotPassword.tsx
@@ -0,0 +1,69 @@
+import { useState, type FormEvent } from "react";
+import { Link, useNavigate } from "react-router-dom";
+import Button from "@/shared/ui/Button";
+import "./ForgotPassword.css";
+
+export default function ForgotPassword() {
+	const navigate = useNavigate();
+	const [email, setEmail] = useState("");
+	const [error, setError] = useState<string | null>(null);
+
+	const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
+		event.preventDefault();
+
+		if (!email.trim()) {
+			setError("Enter the email linked to your account");
+			return;
+		}
+
+		setError(null);
+		navigate("/confirm-email", {
+			state: {
+				email: email.trim(),
+				flow: "recovery",
+			},
+		});
+	};
+
+	return (
+		<main className="forgot-password-page">
+			<section className="forgot-password-shell card card-code-gradient">
+				<div className="forgot-password-copy">
+					<p className="forgot-password-kicker">Password recovery</p>
+					<h1 className="forgot-password-title">Forgot your password?</h1>
+					<p className="forgot-password-text">
+						Enter your email and continue with the verification code
+						flow.
+					</p>
+				</div>
+
+				<form className="forgot-password-form" onSubmit={handleSubmit}>
+					<label className="forgot-password-label" htmlFor="forgot-email">
+						Email
+					</label>
+					<input
+						id="forgot-email"
+						type="email"
+						className="input forgot-password-input"
+						placeholder="Enter your email"
+						value={email}
+						onChange={(event) => setEmail(event.target.value)}
+						autoComplete="email"
+						required
+					/>
+
+					{error && <p className="forgot-password-error">{error}</p>}
+
+					<div className="forgot-password-actions">
+						<Button className="forgot-password-submit" type="submit">
+							Send code
+						</Button>
+						<Link className="forgot-password-link" to="/login">
+							Back to login
+						</Link>
+					</div>
+				</form>
+			</section>
+		</main>
+	);
+}
diff --git a/frontend/src/pages/ForgotPasswordPage/index.ts b/frontend/src/pages/ForgotPasswordPage/index.ts
new file mode 100644
index 0000000..59e684f
--- /dev/null
+++ b/frontend/src/pages/ForgotPasswordPage/index.ts
@@ -0,0 +1 @@
+export { default as ForgotPassword } from "./ForgotPassword";
diff --git a/frontend/src/pages/GetEmailCodePage/GetEmailCode.css b/frontend/src/pages/GetEmailCodePage/GetEmailCode.css
index 9acebba..1113382 100644
--- a/frontend/src/pages/GetEmailCodePage/GetEmailCode.css
+++ b/frontend/src/pages/GetEmailCodePage/GetEmailCode.css
@@ -1,51 +1,147 @@
 .code-page {
-  height: 100vh;
+  min-height: calc(100vh - 180px);
+  padding: 48px 24px 72px;
+  display: grid;
+  place-items: center;
 }
 
-.code-wrapper {
-  width: 70%;
- 
+.code-shell {
+  width: min(980px, 100%);
+  padding: 54px 64px 42px;
+  gap: 36px;
+  box-shadow: var(--shadow-soft-lg);
+}
 
+.code-copy {
+  display: flex;
+  flex-direction: column;
+  gap: 14px;
+  max-width: 640px;
 }
 
-.code-card {
-  width: 930px;
-  min-height: 380px;
-  padding: 26px 40px 22px;
+.code-kicker {
+  margin: 0;
+  font-size: 18px;
+  font-weight: 700;
+  letter-spacing: 0.08em;
+  text-transform: uppercase;
+  color: var(--btn-color-light-theme);
 }
 
 .code-title {
-  text-align: center;
-  font-size: 52px;
-  font-weight: 350;
-  margin-bottom: 38px;
+  margin: 0;
+  font-size: clamp(42px, 6vw, 64px);
+  font-weight: 500;
+  line-height: 1.04;
   color: var(--color-text-main);
 }
 
+.code-description,
+.code-email {
+  margin: 0;
+  font-size: 22px;
+  line-height: 1.5;
+  color: var(--color-text-secondary);
+}
+
+.code-email {
+  font-size: 18px;
+}
+
+.code-form {
+  display: flex;
+  flex-direction: column;
+  gap: 18px;
+  max-width: 520px;
+}
+
+.code-label {
+  font-size: 28px;
+  font-weight: 500;
+  color: var(--color-text-main);
+}
+
+.code-input {
+  max-width: none;
+  padding: 22px 26px;
+  font-size: 28px;
+}
+
+.code-actions {
+  display: flex;
+  align-items: flex-start;
+  justify-content: space-between;
+  gap: 24px;
+  margin-top: 10px;
+}
+
 .code-button {
-  margin-top: 50px;
-  font-size: 48px;
+  font-size: 44px;
   font-weight: 350;
   color: var(--color-text-main);
 }
 
 .code-text {
-  text-align: center;
-  font-size: 24px;
-  font-weight: 350;
+  margin: 0;
+  font-size: 18px;
+  font-weight: 400;
   color: var(--color-text-secondary);
-  margin-top: -2px;
 }
 
 .code-link {
-  text-align: center;
-  font-size: 24px;
-  font-weight: 350;
-  color: var(--color-text-secondary);
+  padding: 0;
+  font-size: 18px;
+  font-weight: 600;
+  color: var(--btn-color-light-theme);
   text-decoration: none;
+  background: transparent;
+  border: 0;
+  cursor: pointer;
 }
 
-.image-placeholder {
-  width: 400px;
-  height: 500px;
+.code-link:hover,
+.code-back-link:hover {
+  color: var(--color-link-hover);
+}
+
+.code-secondary-actions {
+  display: flex;
+  flex-direction: column;
+  align-items: flex-start;
+  gap: 4px;
+}
+
+.code-resent,
+.code-error {
+  font-size: 16px;
+}
+
+.code-resent {
+  color: #145f39;
+}
+
+.code-error {
+  margin: 0;
+  color: #b42318;
+}
+
+.code-back-link {
+  font-size: 18px;
+  font-weight: 600;
+  color: var(--btn-color-light-theme);
+  text-decoration: none;
+}
+
+@media (max-width: 720px) {
+  .code-page {
+    padding-inline: 16px;
+  }
+
+  .code-shell {
+    padding: 36px 24px;
+  }
+
+  .code-actions {
+    flex-direction: column;
+  }
 }
diff --git a/frontend/src/pages/GetEmailCodePage/GetEmailCode.tsx b/frontend/src/pages/GetEmailCodePage/GetEmailCode.tsx
index 559ae05..58ef3e2 100644
--- a/frontend/src/pages/GetEmailCodePage/GetEmailCode.tsx
+++ b/frontend/src/pages/GetEmailCodePage/GetEmailCode.tsx
@@ -1,35 +1,122 @@
-
+import { useMemo, useState, type FormEvent } from "react";
+import { Link, useLocation, useNavigate } from "react-router-dom";
 import "./GetEmailCode.css";
 
+type FlowMode = "registration" | "recovery";
+
+type LocationState = {
+	email?: string;
+	flow?: FlowMode;
+};
+
 export default function CodePage() {
-  return (
-    <div className="code-page flex-center">
-      <div className="code-wrapper flex-between-center">
-        <div className="code-card card card-code-gradient">
-          <h1 className="code-title">Enter the code</h1>
-
-          <form className="flex-col-center">
-            <input
-              type="text"
-              placeholder="Enter text"
-              className="input input-compact"
-            />
-
-            <button type="submit" className="btn-ghost code-button">
-              Next
-            </button>
-          </form>
-
-          <p className="code-text">Didn't receive the code?</p>
-          <a href="#" className="code-link">
-            Resend it?
-          </a>
-        </div>
-
-        <div className="image-placeholder">
-          {/* Здесь позже будет картинка */}
-        </div>
-      </div>
-    </div>
-  );
-}
\ No newline at end of file
+	const navigate = useNavigate();
+	const location = useLocation();
+	const [code, setCode] = useState("");
+	const [error, setError] = useState<string | null>(null);
+	const [resent, setResent] = useState(false);
+
+	const state = (location.state as LocationState | null) ?? null;
+	const flow = state?.flow ?? "registration";
+
+	const pageCopy = useMemo(
+		() =>
+			flow === "recovery"
+				? {
+						kicker: "Password recovery",
+						title: "Check your email",
+						description:
+							"Enter the verification code to continue recovering access to your account.",
+				  }
+				: {
+						kicker: "Registration",
+						title: "Confirm your email",
+						description:
+							"Enter the verification code to continue the account setup flow.",
+				  },
+		[flow],
+	);
+
+	const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
+		event.preventDefault();
+
+		if (!/^\d{4,6}$/.test(code.trim())) {
+			setError("Enter a valid verification code");
+			return;
+		}
+
+		setError(null);
+		navigate("/login", {
+			replace: true,
+			state: {
+				notice:
+					flow === "recovery"
+						? "Code accepted in the UI flow. Continue from login."
+						: "Registration completed. You can sign in now.",
+			},
+		});
+	};
+
+	return (
+		<main className="code-page">
+			<section className="code-shell card card-code-gradient">
+				<div className="code-copy">
+					<p className="code-kicker">{pageCopy.kicker}</p>
+					<h1 className="code-title">{pageCopy.title}</h1>
+					<p className="code-description">{pageCopy.description}</p>
+					{state?.email && (
+						<p className="code-email">Code destination: {state.email}</p>
+					)}
+				</div>
+
+				<form className="code-form" onSubmit={handleSubmit}>
+					<label className="code-label" htmlFor="verification-code">
+						Verification code
+					</label>
+					<input
+						id="verification-code"
+						type="text"
+						placeholder="Enter code"
+						className="input code-input"
+						value={code}
+						onChange={(event) => setCode(event.target.value)}
+						inputMode="numeric"
+						autoComplete="one-time-code"
+						required
+					/>
+
+					{error && <p className="code-error">{error}</p>}
+
+					<div className="code-actions">
+						<button type="submit" className="btn-ghost code-button">
+							Next
+						</button>
+
+						<div className="code-secondary-actions">
+							<p className="code-text">Didn't receive the code?</p>
+							<button
+								type="button"
+								className="code-link"
+								onClick={() => setResent(true)}
+							>
+								Resend it
+							</button>
+							{resent && (
+								<span className="code-resent">
+									A new code request was prepared in the UI flow.
+								</span>
+							)}
+						</div>
+					</div>
+				</form>
+
+				<Link
+					className="code-back-link"
+					to={flow === "recovery" ? "/forgot-password" : "/Registration"}
+				>
+					Back
+				</Link>
+			</section>
+		</main>
+	);
+}
diff --git a/frontend/src/pages/LoginPage/Login.css b/frontend/src/pages/LoginPage/Login.css
index c219228..23fd6da 100644
--- a/frontend/src/pages/LoginPage/Login.css
+++ b/frontend/src/pages/LoginPage/Login.css
@@ -35,6 +35,21 @@
 	gap: 25px;
 }
 
+.login-notice,
+.login-error {
+	margin: 0;
+	font-size: 18px;
+	line-height: 1.5;
+}
+
+.login-notice {
+	color: #145f39;
+}
+
+.login-error {
+	color: #b42318;
+}
+
 .headers-login {
 	margin-top: -10px;
 	font-size: 62px;
diff --git a/frontend/src/pages/LoginPage/Login.tsx b/frontend/src/pages/LoginPage/Login.tsx
index d615586..b36250e 100644
--- a/frontend/src/pages/LoginPage/Login.tsx
+++ b/frontend/src/pages/LoginPage/Login.tsx
@@ -2,12 +2,18 @@ import "./Login.css";
 import st from "../../shared/assets/images/svg/nextBtn.svg";
 import { login_request } from "@/features";
 import { useState, type FormEvent } from "react";
-import { useNavigate } from "react-router-dom";
+import { Link, useLocation, useNavigate } from "react-router-dom";
 import { useAuth } from "@/features/AutchContext/AuthContext";
 
+type LoginLocationState = {
+	notice?: string;
+};
+
 function Login() {
 	const navigate = useNavigate();
+	const location = useLocation();
 	const { refreshAuth } = useAuth();
+	const notice = (location.state as LoginLocationState | null)?.notice;
 
 	const [password, setPassword] = useState("");
 	const [identity, setIdentity] = useState("");
@@ -73,6 +79,7 @@ function Login() {
 				</div>
 
 				{error && <p className="login-error">{error}</p>}
+				{notice && <p className="login-notice">{notice}</p>}
 
 				<button
 					className="btn-ghost next-btn-login"
@@ -82,12 +89,12 @@ function Login() {
 					<img src={st} alt="next" />
 				</button>
 
-				<a className="forgot-password-login" href="#">
+				<Link className="forgot-password-login" to="/forgot-password">
 					Forgot password?
-				</a>
+				</Link>
 			</form>
 		</main>
 	);
 }
 
-export default Login;
\ No newline at end of file
+export default Login;
diff --git a/frontend/src/pages/ProfilePage/Profile.tsx b/frontend/src/pages/ProfilePage/Profile.tsx
index 1bd6caf..ff317a0 100644
--- a/frontend/src/pages/ProfilePage/Profile.tsx
+++ b/frontend/src/pages/ProfilePage/Profile.tsx
@@ -1,6 +1,6 @@
 import { useState, useEffect, useRef, type ChangeEvent } from "react";
 import "./Profile.css";
-import { Button, ProfileImg } from "@/shared";
+import { ProfileImg } from "@/shared";
 import { LowerRank } from "@/shared";
 import { StaticProfileImg } from "@/shared";
 import type { Profile } from "./lib/profileInterface";
@@ -91,6 +91,22 @@ export default function Profile() {
 		setCurrentImg(newUrl);
 	};
 
+	const formatDate = (value: string | null) => {
+		if (!value) {
+			return "n/a";
+		}
+
+		const date = new Date(value);
+		if (Number.isNaN(date.getTime())) {
+			return value;
+		}
+
+		return new Intl.DateTimeFormat("en-GB", {
+			dateStyle: "medium",
+			timeStyle: "short",
+		}).format(date);
+	};
+
 	if (loading) {
 		return <div>Loading...</div>;
 	}
@@ -134,10 +150,14 @@ export default function Profile() {
 						<span className="value">{profile.email}</span>
 
 						<span className="label">Member Since:</span>
-						<span className="value">{profile.memberSince}</span>
+						<span className="value">
+							{formatDate(profile.memberSince)}
+						</span>
 
 						<span className="label">Last Seen:</span>
-						<span className="value">{profile.lastSeen}</span>
+						<span className="value">
+							{formatDate(profile.lastSeen)}
+						</span>
 
 						<span className="label">Now is online</span>
 						<span className="value">
@@ -174,19 +194,23 @@ export default function Profile() {
 						</span>
 					</div>
 					<div className="flex margin-task-complete">
-						<span>
-							Task completed:
-							<li>Easy: {profile.tasksCompleted.easy}</li>
-							<li>Medium: {profile.tasksCompleted.medium}</li>
-							<li>Hard: {profile.tasksCompleted.hard}</li>
-						</span>
+						<div>
+							<span>Task completed:</span>
+							<ul>
+								<li>Easy: {profile.tasksCompleted.easy}</li>
+								<li>Medium: {profile.tasksCompleted.medium}</li>
+								<li>Hard: {profile.tasksCompleted.hard}</li>
+							</ul>
+						</div>
+					</div>
+					<div>
+						<span>Average grade:</span>
+						<ul>
+							<li>Easy: {profile.averageGrade.easy}</li>
+							<li>Medium: {profile.averageGrade.medium}</li>
+							<li>Hard: {profile.averageGrade.hard}</li>
+						</ul>
 					</div>
-					<span>
-						Average grade:
-						<li>Easy: {profile.averageGrade.easy}</li>
-						<li>Medium: {profile.averageGrade.medium}</li>
-						<li>Hard: {profile.averageGrade.hard}</li>
-					</span>
 				</div>
 				<img
 					src={StaticProfileImg}
diff --git a/frontend/src/pages/ProfilePage/lib/profileInterface.ts b/frontend/src/pages/ProfilePage/lib/profileInterface.ts
index 772c104..54da365 100644
--- a/frontend/src/pages/ProfilePage/lib/profileInterface.ts
+++ b/frontend/src/pages/ProfilePage/lib/profileInterface.ts
@@ -1,7 +1,7 @@
 export type Profile = {
 	email: string;
 	username: string;
-	lastSeen: string;
+	lastSeen: string | null;
 	memberSince: string;
 	avatarUrl?: string;
 	isOnline: boolean;
diff --git a/frontend/src/pages/RegistrationPage/Registration.css b/frontend/src/pages/RegistrationPage/Registration.css
index b3b07fe..1dd7392 100644
--- a/frontend/src/pages/RegistrationPage/Registration.css
+++ b/frontend/src/pages/RegistrationPage/Registration.css
@@ -35,6 +35,11 @@
   max-width: 450px;
 }
 
+.registration-error {
+  margin: 0;
+  font-size: 18px;
+  color: #b42318;
+}
 
 .btn-submit-registration {
   position: absolute;
@@ -43,4 +48,4 @@
   font-size: 44px;
   font-weight: 10;
   color: var(--color-text-main);
-}
\ No newline at end of file
+}
diff --git a/frontend/src/pages/RegistrationPage/Registration.tsx b/frontend/src/pages/RegistrationPage/Registration.tsx
index 95947d3..9f8f098 100644
--- a/frontend/src/pages/RegistrationPage/Registration.tsx
+++ b/frontend/src/pages/RegistrationPage/Registration.tsx
@@ -1,21 +1,46 @@
-import { useState } from "react";
+import { useState, type FormEvent } from "react";
 import "./Registration.css";
 import { register_request } from "@/features/registr/registr-request";
+import { useNavigate } from "react-router-dom";
 
 function Registration() {
+	const navigate = useNavigate();
 	const [username, setUsername] = useState("");
 	const [email, setEmail] = useState("");
 	const [password, setPassword] = useState("");
 	const [confirmPassword, setConfirmPassword] = useState("");
+	const [error, setError] = useState<string | null>(null);
+	const [isSubmitting, setIsSubmitting] = useState(false);
 
-	const handleSubmit = async (e: React.FormEvent) => {
+	const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
 		e.preventDefault();
 
+		if (password !== confirmPassword) {
+			setError("Passwords do not match");
+			return;
+		}
+
 		try {
-			alert("Registration successful!");
-			await register_request(username, email, password);
+			setError(null);
+			setIsSubmitting(true);
+
+			const response = await register_request(username, email, password);
+
+			navigate("/confirm-email", {
+				state: {
+					email: response.user.email,
+					flow: "registration",
+				},
+			});
 		} catch (error) {
 			console.error(error);
+			setError(
+				error instanceof Error
+					? error.message
+					: "Registration failed",
+			);
+		} finally {
+			setIsSubmitting(false);
 		}
 	};
 
@@ -34,17 +59,21 @@ function Registration() {
 							type="text"
 							placeholder="Enter username"
 							className="input form-input"
+							value={username}
 							onChange={(e) => setUsername(e.target.value)}
+							required
 						/>
 					</label>
 
 					<label className="form-label">
 						Email
 						<input
-							type="text"
+							type="email"
 							placeholder="Enter email"
 							className="input form-input"
+							value={email}
 							onChange={(e) => setEmail(e.target.value)}
+							required
 						/>
 					</label>
 					<label className="form-label">
@@ -53,7 +82,9 @@ function Registration() {
 							type="password"
 							placeholder="Enter password"
 							className="input form-input"
+							value={password}
 							onChange={(e) => setPassword(e.target.value)}
+							required
 						/>
 					</label>
 
@@ -63,20 +94,20 @@ function Registration() {
 							type="password"
 							placeholder="Confirm your password"
 							className="input form-input"
-							onChange={(e) => {
-								setConfirmPassword(e.target.value);
-								if (confirmPassword !== password) {
-									console.log("Incorrect password!");
-								}
-							}}
+							value={confirmPassword}
+							onChange={(e) => setConfirmPassword(e.target.value)}
+							required
 						/>
 					</label>
 
+					{error && <p className="registration-error">{error}</p>}
+
 					<button
 						type="submit"
 						className="btn-ghost btn-submit-registration"
+						disabled={isSubmitting}
 					>
-						Get code
+						{isSubmitting ? "Creating..." : "Get code"}
 					</button>
 				</form>
 			</div>
diff --git a/frontend/src/pages/SolutionResultPage/SolutionResult.css b/frontend/src/pages/SolutionResultPage/SolutionResult.css
index cf3b7df..a00bb24 100644
--- a/frontend/src/pages/SolutionResultPage/SolutionResult.css
+++ b/frontend/src/pages/SolutionResultPage/SolutionResult.css
@@ -86,10 +86,11 @@
 	display: flex;
 	flex-direction: column;
 	align-items: center;
-	gap: 2px;
+	gap: 4px;
 
 	margin: 0;
 	font-size: 14px;
+	color: var(--color-text-secondary);
 }
 
 .solution-link {
@@ -129,6 +130,31 @@
 	font-weight: 500;
 }
 
+.result-supporting-copy {
+	margin: 16px 0 0;
+	font-size: 18px;
+	line-height: 1.5;
+	color: var(--color-text-secondary);
+}
+
+.result-test-list {
+	display: flex;
+	flex-direction: column;
+	gap: 10px;
+	margin: 28px 0 0;
+	padding: 0;
+	list-style: none;
+	font-size: 17px;
+}
+
+.result-test-list li {
+	display: flex;
+	justify-content: space-between;
+	gap: 24px;
+	padding-bottom: 8px;
+	border-bottom: 1px solid rgba(93, 114, 147, 0.18);
+}
+
 .code-preview-panel {
 	position: relative;
 	min-height: 590px;
@@ -148,17 +174,64 @@
 	pointer-events: none;
 }
 
+.code-preview-header {
+	position: relative;
+	z-index: 1;
+	display: flex;
+	justify-content: space-between;
+	gap: 16px;
+	padding: 28px 32px 0;
+	font-size: 15px;
+	font-weight: 700;
+	letter-spacing: 0.08em;
+	text-transform: uppercase;
+	color: var(--btn-color-light-theme);
+}
+
 .code-preview-panel pre {
 	position: relative;
 	z-index: 1;
 	margin: 0;
-	padding: 180px 32px 26px 32px;
+	padding: 32px;
 	color: rgba(17, 17, 17, 0.56);
 	font-size: 15px;
 	line-height: 1.55;
 	white-space: pre-wrap;
 }
 
+.solution-empty-state {
+	max-width: 760px;
+	margin: 0 auto;
+	padding: 64px 56px;
+	text-align: center;
+	box-shadow: var(--shadow-soft-lg);
+}
+
+.solution-empty-state h1 {
+	margin: 0 0 18px;
+	font-size: clamp(34px, 5vw, 52px);
+	font-weight: 500;
+	color: var(--color-text-main);
+}
+
+.solution-empty-state p {
+	margin: 0 0 24px;
+	font-size: 20px;
+	line-height: 1.6;
+	color: var(--color-text-secondary);
+}
+
+.solution-empty-link {
+	color: var(--btn-color-light-theme);
+	font-size: 20px;
+	font-weight: 600;
+	text-decoration: none;
+}
+
+.solution-empty-link:hover {
+	color: var(--color-link-hover);
+}
+
 @media (max-width: 1100px) {
 	.solution-result-layout {
 		grid-template-columns: 1fr;
diff --git a/frontend/src/pages/SolutionResultPage/SolutionResult.tsx b/frontend/src/pages/SolutionResultPage/SolutionResult.tsx
index 17a5dce..e203467 100644
--- a/frontend/src/pages/SolutionResultPage/SolutionResult.tsx
+++ b/frontend/src/pages/SolutionResultPage/SolutionResult.tsx
@@ -1,45 +1,22 @@
 import type { CSSProperties } from "react";
 import "./SolutionResult.css";
 import svgMatrix from "@/shared/assets/images/svg/matrix-static-dense-gray-transparent.svg";
-import { useLocation } from "react-router-dom";
+import { Link, useLocation } from "react-router-dom";
+import type { SolutionResultsProps } from "@/features/getScoreForSolution/getScoreForSolution";
 
 type LocationState = {
-	Architecture: number;
-	CodeLogic: number;
-	Standards: number;
+	result?: SolutionResultsProps;
+	code?: string;
+	taskTitle?: string;
 };
 
-const codePreview = `function validateUser(payload) {
-  const errors = [];
-
-  if (!payload.email || !payload.email.includes("@")) {
-    errors.push("Invalid email");
-  }
-
-  if (payload.password.length < 8) {
-    errors.push("Password is too short");
-  }
-
-  return {
-    valid: errors.length === 0,
-    errors,
-  };
-}`;
-
 export default function SolutionResult() {
 	const location = useLocation();
 	const state = location.state as LocationState | null;
-
-	const scoreItems = [
-		{ label: "Architecture", value: state?.Architecture ?? 0 },
-		{ label: "Code logic", value: state?.CodeLogic ?? 0 },
-		{ label: "Standards", value: state?.Standards ?? 0 },
-	];
-
-	const avgScore = Math.round(
-		scoreItems.reduce((sum, item) => sum + item.value, 0) /
-			scoreItems.length,
-	);
+	const result = state?.result;
+	const testsCheck = result?.checks.find((check) => check.checkType === "tests");
+	const testDetails = testsCheck?.report.details ?? [];
+	const avgScore = result?.overallScore ?? 0;
 
 	const getPoints = () => {
 		const score = Math.min(avgScore, 100);
@@ -55,6 +32,42 @@ export default function SolutionResult() {
 		"--score-percent": `${avgScore}%`,
 	} as CSSProperties;
 
+	if (!result) {
+		return (
+			<section className="solution-result-page">
+				<div className="solution-empty-state card card-code-gradient">
+					<h1>No submission result yet</h1>
+					<p>
+						Run and submit a task first, then this page will show the
+						backend response for your solution.
+					</p>
+					<Link to="/ChooseTask" className="solution-empty-link">
+						Go to task selection
+					</Link>
+				</div>
+			</section>
+		);
+	}
+
+	const scoreItems = [
+		{ label: "Status", value: result.submission.status },
+		{ label: "Tests passed", value: `${result.testsPassed}/${result.totalTests}` },
+		{
+			label: "Runtime",
+			value:
+				result.submission.executionTimeMs !== null
+					? `${result.submission.executionTimeMs} ms`
+					: "n/a",
+		},
+		{
+			label: "Memory",
+			value:
+				result.submission.memoryUsedKb !== null
+					? `${result.submission.memoryUsedKb} KB`
+					: "n/a",
+		},
+	];
+
 	return (
 		<section className="solution-result-page">
 			<div className="solution-result-layout">
@@ -66,38 +79,57 @@ export default function SolutionResult() {
 
 						<div className="score-details">
 							<p className="score-kicker">
-								Your code is {avgScore} % correct
+								{state?.taskTitle || "Submission"} scored {avgScore} %
 							</p>
 
 							<ul className="score-list">
 								{scoreItems.map((item) => (
-									<div key={item.label}>
+									<li key={item.label}>
 										<span>{item.label} </span>
-										<span>{item.value} %</span>
-									</div>
+										<strong>{item.value}</strong>
+									</li>
 								))}
 							</ul>
 						</div>
-						{/*TODO: Feature func*/}
-						{/* <div className="solution-action">
-							<button className="solution-link">
-								AI Analysis
-							</button>
-							<span>Learn more about errors</span>
-						</div> */}
+						<div className="solution-action">
+							<span>{result.submission.language}</span>
+							<span>
+								Checked {result.submission.checkedAt ? "successfully" : "pending"}
+							</span>
+						</div>
 					</div>
 
 					<div className="result-message">
 						<h1>
 							You have been awarded {getPoints()} for this task
 						</h1>
+						<p className="result-supporting-copy">
+							{result.failedTests === 0
+								? "All available backend checks passed."
+								: `${result.failedTests} test(s) still need attention.`}
+						</p>
+
+						{testDetails.length > 0 && (
+							<ul className="result-test-list">
+								{testDetails.map((detail) => (
+									<li key={detail.name}>
+										<span>{detail.name}</span>
+										<strong>{detail.status}</strong>
+									</li>
+								))}
+							</ul>
+						)}
 					</div>
 				</div>
 
 				<div className="code-preview-panel">
 					<img src={svgMatrix} alt="" className="result-matrix-bg" />
+					<div className="code-preview-header">
+						<span>Submitted code</span>
+						<span>#{result.submission.id}</span>
+					</div>
 					<pre aria-label="Solution preview">
-						<code>{codePreview}</code>
+						<code>{state?.code || "No code preview available"}</code>
 					</pre>
 				</div>
 			</div>
diff --git a/frontend/src/pages/index.ts b/frontend/src/pages/index.ts
index 2c40a1a..724655c 100644
--- a/frontend/src/pages/index.ts
+++ b/frontend/src/pages/index.ts
@@ -7,6 +7,7 @@ export { Login } from "./LoginPage/index.ts";
 export { CodeEditor } from "./CodeBlockPage/index.ts";
 export { Registration } from "./RegistrationPage/index.ts";
 export { CodePage } from "./GetEmailCodePage/index.ts";
+export { ForgotPassword } from "./ForgotPasswordPage/index.ts";
 export { ChooseTask } from "./ChooseTaskPage/index.ts";
 export { Profile } from "./ProfilePage/index.ts";
-export { SolutionResult } from "./SolutionResultPage/index.ts";
\ No newline at end of file
+export { SolutionResult } from "./SolutionResultPage/index.ts";
diff --git a/frontend/src/shared/api/getErrorMessage.ts b/frontend/src/shared/api/getErrorMessage.ts
new file mode 100644
index 0000000..e28ee51
--- /dev/null
+++ b/frontend/src/shared/api/getErrorMessage.ts
@@ -0,0 +1,41 @@
+type ErrorPayload = {
+	detail?: string | Array<{ msg?: string }>;
+	message?: string;
+};
+
+export async function getErrorMessage(
+	response: Response,
+	fallbackMessage: string,
+): Promise<string> {
+	try {
+		const data = (await response.clone().json()) as ErrorPayload;
+
+		if (typeof data.message === "string" && data.message.trim()) {
+			return data.message;
+		}
+
+		if (typeof data.detail === "string" && data.detail.trim()) {
+			return data.detail;
+		}
+
+		if (Array.isArray(data.detail)) {
+			const validationMessage = data.detail
+				.map((item) => item.msg?.trim())
+				.filter(Boolean)
+				.join(", ");
+
+			if (validationMessage) {
+				return validationMessage;
+			}
+		}
+	} catch {}
+
+	try {
+		const text = await response.clone().text();
+		if (text.trim()) {
+			return text;
+		}
+	} catch {}
+
+	return fallbackMessage;
+}
diff --git a/frontend/src/shared/types/routes.ts b/frontend/src/shared/types/routes.ts
index 41d278d..d1a2b22 100644
--- a/frontend/src/shared/types/routes.ts
+++ b/frontend/src/shared/types/routes.ts
@@ -1,4 +1,4 @@
-import { ComponentType } from "react";
+import type { ComponentType } from "react";
 
 export type AppPage = {
 	path: string;
diff --git a/frontend/src/shared/ui/Button.tsx b/frontend/src/shared/ui/Button.tsx
index f6ebb1e..1a7be4a 100644
--- a/frontend/src/shared/ui/Button.tsx
+++ b/frontend/src/shared/ui/Button.tsx
@@ -20,7 +20,7 @@ export default function Button({
 	return (
 		<button
 			type={type}
-			className={`specific-btn ${className}`}
+			className={`specific-btn specific-btn--${variant} ${className}`}
 			onClick={onClick}
 			disabled={disabled}
 		>
diff --git a/frontend/tsconfig.app.json b/frontend/tsconfig.app.json
index 6afa9be..08e5a15 100644
--- a/frontend/tsconfig.app.json
+++ b/frontend/tsconfig.app.json
@@ -29,4 +29,5 @@
     "noUncheckedSideEffectImports": true
   },
   "include": ["src"],
+  "exclude": ["src/**/*.test.ts", "src/**/*.test.tsx", "src/setupTests.ts"]
 }
