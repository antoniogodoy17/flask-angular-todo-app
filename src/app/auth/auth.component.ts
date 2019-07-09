import { Component, OnInit } from '@angular/core';
import { FormGroup, FormControl, Validators } from '@angular/forms';
import { AuthService } from '../services/auth.service';
import { Router } from '@angular/router';

declare let $: any;

@Component({
  selector: 'app-auth',
  templateUrl: './auth.component.html',
  styleUrls: ['./auth.component.sass']
})
export class AuthComponent implements OnInit {
  loginForm: FormGroup;
  signupForm: FormGroup;

  constructor(private authService: AuthService,
              private router: Router) { }

  ngOnInit() {
    if (this.authService.isLoggedIn()) {
      this.router.navigate(['']);
    }
    this.initForms();
  }

  initForms() {
    this.loginForm = new FormGroup({
      email: new FormControl(null, [Validators.required]),
      password: new FormControl(null, [Validators.required])
    });

    this.signupForm = new FormGroup({
      email: new FormControl(null, [Validators.required]),
      password: new FormControl(null, [Validators.required]),
      confirm_password: new FormControl(null, [Validators.required])
    });
  }

  onLogin() {
    const credentials = {
      email: this.loginForm.controls.email.value,
      password: this.loginForm.controls.password.value
    };

    this.authService.login(credentials).subscribe(res => {
      if (res.errorCode === 0) {
        this.authService.setSession(res.token);
        this.router.navigate(['']);
      }
    });
  }

  onSignup() {
    const credentials = {
      email: this.signupForm.controls.email.value,
      password: this.signupForm.controls.password.value
    };

    this.authService.signup(credentials).subscribe(res => {
      if (res.errorCode === 0) {
        $('.ui.basic.modal')
          .modal({
            onHide: () => {
              this.signupForm.reset();
            }
          })
          .modal('show');
      }
    });
  }

}
