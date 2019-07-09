import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { JwtHelperService } from '@auth0/angular-jwt';

@Injectable({
  providedIn: 'root'
})
export class AuthService {

  private APIURL = 'http://localhost:8080/auth/';
  private jwt = new JwtHelperService();
  token;

  constructor(private http: HttpClient) {
    this.token = sessionStorage.getItem('todoapp-token');
  }

  isLoggedIn(): boolean {
    const token = sessionStorage.getItem('todoapp-token');
    if (token) {
      if (!this.jwt.isTokenExpired(this.token)) {
        return true;
      } else {
        return false;
      }
    } else {
      return false;
    }
  }

  setSession(token: string) {
    this.token = token;
    sessionStorage.setItem('todoapp-token', token);
  }

  logout() {
    sessionStorage.removeItem('todoapp-token');
    this.token = null;
  }

  login(credentials: any) {
    return this.http.post<{ message: string, errorCode: number, user: any, token: string }>(`${this.APIURL}login`, credentials);
  }

  signup(credentials: any) {
    return this.http.post<{ message: string, errorCode: number, user: any }>(`${this.APIURL}signup`, credentials);
  }

}
