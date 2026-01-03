import { Injectable } from "@angular/core";
import { BehaviorSubject, Observable, tap } from "rxjs";
import { ApiService } from "./api.service";
import { User, AuthResponse } from "../models/models";

@Injectable({
  providedIn: "root",
})
export class AuthService {
  private userSubject = new BehaviorSubject<User | null>(null);
  user$ = this.userSubject.asObservable();

  constructor(private api: ApiService) {
    this.loadUser();
  }

  private loadUser() {
    const userJson = localStorage.getItem("user");
    if (userJson) {
      this.userSubject.next(JSON.parse(userJson));
    }
  }

  get currentUser(): User | null {
    return this.userSubject.value;
  }

  get isLoggedIn(): boolean {
    return !!this.userSubject.value;
  }

  get token(): string | null {
    return this.userSubject.value?.token || null;
  }

  register(data: any): Observable<AuthResponse> {
    return this.api.register(data).pipe(
      tap((response) => {
        if (response.user) {
          this.setUser(response.user);
        }
      })
    );
  }

  login(data: any): Observable<AuthResponse> {
    return this.api.login(data).pipe(
      tap((response) => {
        if (response.user) {
          this.setUser(response.user);
        }
      })
    );
  }

  logout() {
    localStorage.removeItem("user");
    this.userSubject.next(null);
  }

  private setUser(user: User) {
    localStorage.setItem("user", JSON.stringify(user));
    this.userSubject.next(user);
  }
}
