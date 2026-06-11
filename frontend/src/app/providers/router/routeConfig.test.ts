import { describe, expect, it } from "vitest";
import { mainPageRoutes } from "./routeConfig";

describe("mainPageRoutes", () => {
	it("defines all key frontend routes with the expected access mode", () => {
		const accessByPath = new Map(
			mainPageRoutes.map((route) => [route.path, route.access]),
		);

		expect(accessByPath.get("/")).toBe("public");
		expect(accessByPath.get("/login")).toBe("guest");
		expect(accessByPath.get("/Registration")).toBe("guest");
		expect(accessByPath.get("/forgot-password")).toBe("guest");
		expect(accessByPath.get("/reset-password")).toBe("guest");
		expect(accessByPath.get("/ChooseTask")).toBe("private");
		expect(accessByPath.get("/CodeBlock")).toBe("private");
		expect(accessByPath.get("/profile")).toBe("private");
		expect(accessByPath.get("/result")).toBe("private");
	});

	it("keeps main navigation pages visible in the navbar", () => {
		const navbarPaths = mainPageRoutes
			.filter((route) => route.showInNavbar)
			.map((route) => route.path);

		expect(navbarPaths).toContain("/");
		expect(navbarPaths).toContain("/login");
		expect(navbarPaths).toContain("/Registration");
		expect(navbarPaths).toContain("/ChooseTask");
		expect(navbarPaths).toContain("/profile");
		expect(navbarPaths).not.toContain("/confirm-email");
		expect(navbarPaths).not.toContain("/CodeBlock");
		expect(navbarPaths).not.toContain("/result");
	});
});
