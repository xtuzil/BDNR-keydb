import { ChangeDetectorRef, Component } from '@angular/core';
import { FormControl } from '@angular/forms';
import { Observable, Subscription } from 'rxjs';
import { AppService, Message } from './app.service';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss'],
})
export class AppComponent {
  title = 'chat';
  username = '';
  usernameControl = new FormControl('');
  messages: string[] = [];
  selectedRoom: string = '';

  constructor(private service: AppService) {}

  ngOnInit() {
    this.username = localStorage.getItem('Username') ?? '';
  }

  setUsername() {
    console.log(this.usernameControl.value);
    this.username = this.usernameControl.value ?? '';
    localStorage.setItem('Username', this.username);
  }

  logout() {
    localStorage.removeItem('Username');
    this.username = '';
  }

  select(room_code: string) {
    this.selectedRoom = room_code;
    console.log('SELECTED ROOM: ', room_code);
    this.service.fetchRoomMessages(room_code);
  }
}
