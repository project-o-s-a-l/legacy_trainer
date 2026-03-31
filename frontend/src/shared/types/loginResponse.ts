export type LoginResponse = {
	token: string;
	user: {
		id: number;
		login: string;
	};
};