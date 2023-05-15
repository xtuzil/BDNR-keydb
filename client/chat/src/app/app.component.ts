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
  selectedRoom!: Room | undefined;

  searchWordControl = new FormControl('');
  searching = false;
  searchedMessages$!: Observable<Message[]>;

  constructor(private service: AppService) {}

  ngOnInit() {
    this.username = localStorage.getItem('Username') ?? '';
    this.searchedMessages$ = this.service.searchedMessages.asObservable();
  }

  setUsername() {
    console.log(this.usernameControl.value);
    this.username = this.usernameControl.value ?? '';
    localStorage.setItem('Username', this.username);
  }

  logout() {
    localStorage.removeItem('Username');
    this.selectedRoom = undefined;
    this.username = '';
  }

  select(room: Room) {
    this.selectedRoom = room;
    console.log('SELECTED ROOM: ', room);
    this.service.fetchRoomMessages(room.code);
  }

  search() {
    const searchWord = this.searchWordControl.value ?? '';
    if (searchWord !== '') {
      this.service.search(searchWord);
      this.searching = true;
    }
  }

  cancelSearch() {
    this.searching = false;
    this.searchWordControl.reset();
  }

  leave() {
    console.log('LEAVING ROOM: ', this.selectedRoom?.code);
    this.selectedRoom = undefined;
  }
}
