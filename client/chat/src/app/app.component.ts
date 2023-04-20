import { ChangeDetectorRef, Component } from '@angular/core';
import { FormControl } from '@angular/forms';
import { Observable, Subscription } from 'rxjs';
import { AppService, Message, Room } from './app.service';

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
  selectedRoom!: Room;

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

  select(room: Room) {
    this.selectedRoom = room;
    console.log('SELECTED ROOM: ', room);
    this.service.fetchRoomMessages(room.code);
  }
}
