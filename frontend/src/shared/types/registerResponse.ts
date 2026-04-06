export type RegisterResponse = {
	token?: string;
	user?: {
		id: number,
		username: string,
		email:string
	};
};