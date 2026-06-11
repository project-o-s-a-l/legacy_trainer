import {
	useCallback,
	useEffect,
	useMemo,
	useState,
	type ReactNode,
} from "react";
import { getMe } from "./getMe";
import { API_V1_BASE_URL } from "@/shared/api/config";
import { AuthContext } from "./AuthContext.shared";
import type { User } from "./getMe.types";

export function AuthProvider({ children }: {children: ReactNode}) {
	const [user, setUser] = useState<User | null>(null);
	const [loading, setLoading] = useState(true);

	const refreshAuth = useCallback(async () => {
		try {
			setLoading(true);
			const me = await getMe();
			setUser(me);
		} catch(error) {
			console.error("Auth check failed: ", error);
			setUser(null);
		} finally {
			setLoading(false);
		}
	}, []);

	const logout = useCallback(async () => {
		try {
			await fetch(`${API_V1_BASE_URL}/auth/logout`, {
				method: "POST",
				credentials: "include"
			});

		} catch(error) {
			console.error("Logout error: ", error);
		} finally {
			setUser(null);
		}
	}, []);

	useEffect(() => {
		void refreshAuth();
	}, [refreshAuth]);

	const value = useMemo(
		() => ({
			user,
			isAuthenticated: Boolean(user),
			loading,
			refreshAuth,
			logout
		}),
		[user, loading, refreshAuth, logout]
	);

	return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}
