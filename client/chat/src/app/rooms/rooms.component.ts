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
  roomCodeControl = new FormControl('');

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
      const newRoomName = this.newRoomNameControl.value;
      this.service.createRoom(newRoomName).subscribe((res) => {
        const newRoomCode = res.room_code as string;
        this.newRoomNameControl.reset();
        this.service.fetchUserRooms(localStorage.getItem('Username') ?? '');
        this.select({ name: newRoomName, code: newRoomCode });
      });
    }
  }

  joinRoom() {
    console.log('REGISTER ROOM: ', this.roomCodeControl.value);
    if (this.roomCodeControl.value) {
      const roomCode = this.roomCodeControl.value;
      this.service.joinRoom(roomCode).subscribe(
        (_) => {
          this.roomCodeControl.reset();
          this.service.fetchUserRooms(localStorage.getItem('Username') ?? '');
        },
        (err) => {
          alert(`Error: ${err.error.detail}`);
        }
      );
    }
  }
}
