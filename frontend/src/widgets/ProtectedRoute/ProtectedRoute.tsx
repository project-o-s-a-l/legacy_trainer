import { Navigate } from "react-router-dom";
import { useAuth } from "@/features/AutchContext/AuthContext";
import type { ReactNode } from "react";

type Props = {
	children: ReactNode;
};

export default function ProtectedRoute({ children }: Props) {
	const { isAuthenticated, loading } = useAuth();

	if(loading) {
		return <div>Check auth....</div>
	};

	if(!isAuthenticated) {
		return <Navigate to="/login" />
	}

	return children;
}
