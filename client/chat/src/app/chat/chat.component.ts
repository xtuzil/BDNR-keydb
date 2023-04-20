import { ChangeDetectorRef, Component, Input, OnInit } from '@angular/core';
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

  chatMessages$!: Observable<Message[]>;
  messageControl = new FormControl('');
  message = '';

  constructor(private service: AppService) {}

  ngOnInit(): void {
    this.chatMessages$ = this.service.chatMessages.asObservable();
  }

  sendMessage() {
    this.message = this.messageControl.value ?? '';
    console.log('SENDING MESSAGE: ', this.message);
    this.service.sendMessage(this.room.code, this.message);
    this.messageControl.reset();
  }
}
