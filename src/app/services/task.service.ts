import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Task } from '../models/task';
import { AuthService } from './auth.service';

@Injectable({
  providedIn: 'root'
})
export class TaskService {

  private APIURL = 'http://localhost:8080/api/';

  constructor(private authService: AuthService,
              private http: HttpClient) { }

  getAuthHeaders() {
    const options = {
      headers: new HttpHeaders({
        'Content-Type':  'application/json',
        'Authorization': `Bearer ${this.authService.token}`
      })
    };
    return options;
  }
  getTasks() {
    const options = this.getAuthHeaders();
    return this.http.get<{ message: string, errorCode: number, tasks: any }>(`${this.APIURL}user/tasks`, options);
  }

  createTask(task: Task) {
    const options = this.getAuthHeaders();
    return this.http.post<{ message: string, errorCode: number, task: any }>(`${this.APIURL}tasks`, task, options);
  }

  updateTask(task: Task) {
    const options = this.getAuthHeaders();
    return this.http.put<{ message: string, errorCode: number, task: any }>(`${this.APIURL}tasks/${task._id}`, task, options);
  }

  deleteTask(taskId: string) {
    const options = this.getAuthHeaders();
    return this.http.delete<{ message: string, errorCode: number }>(`${this.APIURL}tasks/${taskId}`, options);
  }
}
