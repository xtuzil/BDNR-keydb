import {
  ChangeDetectorRef,
  Component,
  EventEmitter,
  Input,
  OnInit,
  Output,
} from '@angular/core';
import { FormControl } from '@angular/forms';
import { Observable } from 'rxjs';
import { AppService, Message, Room } from '../app.service';

@Component({
  selector: 'app-chat',
  templateUrl: './chat.component.html',
  styleUrls: ['./chat.component.scss'],
})
export class ChatComponent implements OnInit {
  @Input()
  room!: Room;

  @Output() leaveEvent = new EventEmitter<null>();

  chatMessages$!: Observable<Message[]>;
  messageControl = new FormControl('');
  message = '';

  searchWordControl = new FormControl('');
  searching = false;
  searchedMessages$!: Observable<Message[]>;

  constructor(private service: AppService) {}

  ngOnInit(): void {
    this.chatMessages$ = this.service.chatMessages.asObservable();
    this.searchedMessages$ = this.service.searchedMessages.asObservable();
  }

  sendMessage() {
    this.message = this.messageControl.value ?? '';
    if (this.message !== '') {
      console.log('SENDING MESSAGE: ', this.message);
      this.service.sendMessage(this.room.code, this.message);
      this.messageControl.reset();
    }
  }

  search() {
    const searchWord = this.searchWordControl.value ?? '';
    if (searchWord !== '') {
      this.service.searchInRoom(this.room.code, searchWord);
      this.searching = true;
    }
  }

  cancelSearch() {
    this.searching = false;
    this.searchWordControl.reset();
    this.service.fetchRoomMessages(this.room.code);
  }

  leaveRoom() {
    if (this.room.code) {
      this.service.leaveRoom(this.room.code).subscribe(
        (_) => {
          this.leaveEvent.emit();
          this.service.fetchUserRooms(localStorage.getItem('Username') ?? '');
        },
        (err) => {
          alert(`Error: ${err.error.detail}`);
        }
      );
    }
  }
}
