import { Component, EventEmitter, OnInit, Output } from '@angular/core';
import { FormControl } from '@angular/forms';
import { Observable } from 'rxjs';
import { AppService, Room } from '../app.service';

@Component({
  selector: 'app-rooms',
  templateUrl: './rooms.component.html',
  styleUrls: ['./rooms.component.scss'],
})
export class RoomsComponent implements OnInit {
  rooms$!: Observable<Room[]>;

  @Output() selectedEvent = new EventEmitter<Room>();

  newRoomNameControl = new FormControl('');

  selectedRoom!: Room;

  constructor(private service: AppService) {}

  ngOnInit(): void {
    this.rooms$ = this.service.rooms.asObservable();
    const username = localStorage.getItem('Username') ?? '';
    if (username) {
      this.service.fetchUserRooms(username);
    }
  }

  select(room: Room) {
    this.selectedRoom = room;
    this.selectedEvent.emit(room);
  }

  createRoom() {
    console.log('CREATE ROOM: ', this.newRoomNameControl.value);
    if (this.newRoomNameControl.value) {
      this.service
        .createRoom(this.newRoomNameControl.value)
        .subscribe((res) => {
          this.newRoomNameControl.reset();
          this.service.fetchUserRooms(localStorage.getItem('Username') ?? '');
          this.select(res.room_code);
        });
    }
  }
}
