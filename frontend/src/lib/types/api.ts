export interface ApiError {
	detail: string;
	status_code: number;
}

export interface ApiResponse<T> {
	data: T;
	message?: string;
}

export interface LoginResponse {
	access_token: string;
	token_type: string;
}

export interface RegisterResponse extends LoginResponse {}