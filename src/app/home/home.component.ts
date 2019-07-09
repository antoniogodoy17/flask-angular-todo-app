import { Component, OnInit } from '@angular/core';
import { FormGroup, FormControl } from '@angular/forms';
import { TaskService } from '../services/task.service';
import { Task } from '../models/task';
import { AuthService } from '../services/auth.service';
import { Router } from '@angular/router';

declare let $: any;

@Component({
  selector: 'app-home',
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.sass']
})
export class HomeComponent implements OnInit {
  taskForm: FormGroup;
  tasks: [Task];
  editing = false;
  currentTask: Task = null;

  constructor(private authService: AuthService,
              private taskService: TaskService,
              private router: Router) { }

  ngOnInit() {
    if (!this.authService.isLoggedIn()) {
      this.router.navigate(['auth']);
    }
    $('.ui.accordion').accordion();
    this.initForm();
    this.getTasks();
  }

  initForm() {
    this.taskForm = new FormGroup({
      title: new FormControl(),
      content: new FormControl(),
      due_date: new FormControl()
    });
  }

  logout() {
    this.authService.logout();
    this.router.navigate(['auth']);
  }

  getTasks() {
    this.taskService.getTasks().subscribe(res => {
      if (res.errorCode === 0) {
        this.tasks = res.tasks;
      }
    });
  }

  onSubmit() {
    if (this.editing) {
      this.updateTask();
    } else {
      this.createTask();
    }
  }

  createTask() {
    this.taskService.createTask(this.taskForm.value).subscribe(res => {
      if (res.errorCode === 0){
        this.getTasks();
        this.taskForm.reset();
      } else {
        console.log(res.message);
      }
    });
  }

  fillTask(task: Task) {
    this.currentTask = task;
    this.editing = true;

    this.taskForm.controls.title.patchValue(task.title);
    this.taskForm.controls.content.patchValue(task.content);
    this.taskForm.controls.due_date.patchValue(task.due_date);
  }

  updateTask() {
    const updatedTask: Task = {
      _id: this.currentTask._id,
      ...this.taskForm.value
    };
    this.taskService.updateTask(updatedTask).subscribe(res => {
      if (res.errorCode === 0) {
        this.getTasks();
        this.editing = false;
        this.currentTask = null;
        this.taskForm.reset();
      } else {
        console.log(res.message);
      }
    });
  }

  deleteTask(taskId: string) {
    this.taskService.deleteTask(taskId).subscribe(res => {
      if (res.errorCode === 0) {
        this.getTasks();
      } else {
        console.log(res.message);
      }
    });
  }

}
