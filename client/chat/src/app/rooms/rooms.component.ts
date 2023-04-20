import { Component, EventEmitter, OnInit, Output } from '@angular/core';
import { Observable } from 'rxjs';
import { AppService } from '../app.service';

@Component({
  selector: 'app-rooms',
  templateUrl: './rooms.component.html',
  styleUrls: ['./rooms.component.scss'],
})
export class RoomsComponent implements OnInit {
  rooms$!: Observable<string[]>;

  @Output() selectedEvent = new EventEmitter<string>();

  selectedRoom = '';

  constructor(private service: AppService) {}

  ngOnInit(): void {
    this.rooms$ = this.service.rooms.asObservable();
    const username = localStorage.getItem('Username') ?? '';
    if (username) {
      this.service.fetchUserRooms(username);
    }
  }

  select(room_code: string) {
    this.selectedRoom = room_code;
    this.selectedEvent.emit(room_code);
  }
}
