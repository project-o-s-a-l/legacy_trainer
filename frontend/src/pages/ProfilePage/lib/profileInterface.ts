export type Profile = {
	email: string;
	username: string;
	lastSeen: string;
	memberSince: string;
	avatarUrl?: string;
	isOnline: boolean;
	points: number;
	tasksCompleted: {
		easy: number;
		medium: number;
		hard: number;
	};
	averageGrade: {
		easy: number;
		medium: number;
		hard: number;
	};
};
