import { ChangeDetectorRef, Component, EventEmitter, OnInit, Output } from '@angular/core';
import { FormControl } from '@angular/forms';
import { Observable, Subscription } from 'rxjs';
import { AppService, Room } from '../app.service';

@Component({
  selector: 'app-rooms',
  templateUrl: './rooms.component.html',
  styleUrls: ['./rooms.component.scss'],
})
export class RoomsComponent implements OnInit {
  rooms: Room[] = [];

  @Output() selectedEvent = new EventEmitter<Room>();

  newRoomNameControl = new FormControl('');
  roomCodeControl = new FormControl('');

  selectedRoom!: Room;

  show = true;

  protected messageStreamSub: Subscription | undefined;
  protected roomsSub: Subscription | undefined;

  constructor(private service: AppService, private cdr: ChangeDetectorRef) {}

  ngOnInit(): void {
    this.roomsSub = this.service.rooms.subscribe((rooms) => {
      this.rooms = this.sortRoomsByLastMessage(rooms);
    });
    this.subscribeStream();

    const username = localStorage.getItem('Username') ?? '';
    if (username) {
      this.service.fetchUserRooms(username);
    }
  }

  protected sortRoomsByLastMessage(rooms: Room[]): Room[] {
    return rooms.sort((a, b) => {
      if (a.last_message && b.last_message) {
        return a.last_message.timestamp > b.last_message.timestamp ? -1 : 1;
      } else if (a.last_message) {
        return -1;
      } else if (b.last_message) {
        return 1;
      } else {
        return 0;
      }
    });
  }

  protected subscribeStream(): void {
    this.messageStreamSub = this.service.message.subscribe((msg) => {
      for (let room of this.rooms) {
        if (msg.room_code === room.code) {
          room.last_message = msg;
          break;
        }
      }
      this.rooms = this.sortRoomsByLastMessage(this.rooms);
      this.cdr.detectChanges();
      this.reload();
    });
    this.service.getMessagesStream();
  }

  reload() {
    this.show = false;
    setTimeout(() => this.show = true);
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

  ngOnDestroy(): void {
    this.messageStreamSub?.unsubscribe();
    this.roomsSub?.unsubscribe();
  }
}
