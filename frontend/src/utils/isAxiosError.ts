import { AxiosError } from "axios";

export function isAxiosError<T = unknown>(err: unknown): err is AxiosError<T> {
  return err instanceof AxiosError;
}