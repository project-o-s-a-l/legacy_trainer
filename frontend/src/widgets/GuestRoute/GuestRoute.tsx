import { Navigate } from "react-router-dom";
import { useAuth } from "@/features/AutchContext/AuthContext";
import type { ReactNode } from "react";

type Props = {
	children: ReactNode;
};

export default function GuestRoute({ children }: Props) {
	const { isAuthenticated, loading } = useAuth();

	if (loading) {
		return <div>loading....</div>;
	}

	if (isAuthenticated) {
		return <Navigate to="/profile" replace />;
	}

	return children;
}
