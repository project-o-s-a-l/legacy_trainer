export type RegisterResponse = {
	message: string;
	user: {
		id: number,
		username: string,
		email:string
	};
};
