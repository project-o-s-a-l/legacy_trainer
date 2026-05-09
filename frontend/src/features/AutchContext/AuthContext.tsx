import {
	createContext,
	useCallback,
	useContext,
	useEffect,
	useMemo,
	useState,
	type ReactNode,
} from "react";
import { getMe } from "./getMe";
import type { User } from "./getMe.types";
import { API_V1_BASE_URL } from "@/shared/api/config";

type AuthContextType = {
	user: User | null;
	isAuthenticated: boolean;
	loading: boolean;
	refreshAuth: () => Promise<void>;
	logout: () => Promise<void>;
};

const AuthContext = createContext<AuthContextType | undefined>(undefined);

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

export function useAuth() {
	const context = useContext(AuthContext);

	if(!context) {
		throw new Error("useAuth must be used inside AuthProvider");
	}

	return context;
}