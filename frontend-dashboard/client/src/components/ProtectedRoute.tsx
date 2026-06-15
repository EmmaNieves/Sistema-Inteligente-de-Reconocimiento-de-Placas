import { ReactNode } from "react";
import { Redirect } from "wouter";
import { useAuth } from "@/hooks/use-auth";

interface Props {
  children: ReactNode;
  requiredRole?: "visualizador" | "operador" | "administrador";
}

const ROLE_HIERARCHY: Record<string, number> = {
  visualizador: 1,
  operador: 2,
  administrador: 3,
};

export function ProtectedRoute({ children, requiredRole }: Props) {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen bg-[#253232] flex items-center justify-center">
        <div className="w-8 h-8 border-2 border-[#fc6c03] border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  if (!user) return <Redirect to="/login" />;

  if (requiredRole) {
    const userRank = ROLE_HIERARCHY[user.role] ?? 0;
    const minRank = ROLE_HIERARCHY[requiredRole] ?? 0;
    if (userRank < minRank) return <Redirect to="/dashboard" />;
  }

  return <>{children}</>;
}