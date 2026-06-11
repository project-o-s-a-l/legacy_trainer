import { createContext } from "react";
import type { User } from "./getMe.types";

export type AuthContextType = {
	user: User | null;
	isAuthenticated: boolean;
	loading: boolean;
	refreshAuth: () => Promise<void>;
	logout: () => Promise<void>;
};

export const AuthContext = createContext<AuthContextType | undefined>(
	undefined,
);
